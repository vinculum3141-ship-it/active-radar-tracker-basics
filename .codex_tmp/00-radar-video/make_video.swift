import AppKit
import AVFoundation
import CoreVideo
import Foundation

struct Segment: Decodable {
    let id: String
    let title: String
    let textPath: String
    let audioPath: String
    let imagePath: String
}

func fail(_ message: String) -> Never {
    fputs("\(message)\n", stderr)
    exit(1)
}

guard CommandLine.arguments.count == 3 else {
    fail("Usage: make_video <segments.json> <output.mp4>")
}

let manifestURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])
let tempVideoURL = outputURL.deletingLastPathComponent().appendingPathComponent("00-radar-intuition-silent-video.mp4")
let segments = try JSONDecoder().decode([Segment].self, from: Data(contentsOf: manifestURL))

try? FileManager.default.removeItem(at: tempVideoURL)
try? FileManager.default.removeItem(at: outputURL)

var durations: [Double] = []
for segment in segments {
    let asset = AVURLAsset(url: URL(fileURLWithPath: segment.audioPath))
    let seconds = CMTimeGetSeconds(asset.duration)
    guard seconds.isFinite && seconds > 0.1 else { fail("Invalid audio duration for \(segment.audioPath)") }
    durations.append(seconds)
}
let totalDuration = durations.reduce(0, +)

func pixelBuffer(from imagePath: String, width: Int, height: Int, pool: CVPixelBufferPool) -> CVPixelBuffer {
    guard let image = NSImage(contentsOfFile: imagePath) else { fail("Could not load \(imagePath)") }
    var rect = CGRect(origin: .zero, size: image.size)
    guard let cgImage = image.cgImage(forProposedRect: &rect, context: nil, hints: nil) else { fail("Could not decode \(imagePath)") }
    var optionalBuffer: CVPixelBuffer?
    CVPixelBufferPoolCreatePixelBuffer(nil, pool, &optionalBuffer)
    guard let buffer = optionalBuffer else { fail("Could not allocate video frame") }
    CVPixelBufferLockBaseAddress(buffer, [])
    defer { CVPixelBufferUnlockBaseAddress(buffer, []) }
    guard let context = CGContext(
        data: CVPixelBufferGetBaseAddress(buffer),
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: CVPixelBufferGetBytesPerRow(buffer),
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue
    ) else { fail("Could not create frame context") }
    context.setFillColor(NSColor.white.cgColor)
    context.fill(CGRect(x: 0, y: 0, width: width, height: height))
    context.interpolationQuality = .high
    context.draw(cgImage, in: CGRect(x: 0, y: 0, width: width, height: height))
    return buffer
}

let width = 1280
let height = 720
let writer = try AVAssetWriter(outputURL: tempVideoURL, fileType: .mp4)
let videoSettings: [String: Any] = [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [
        AVVideoAverageBitRateKey: 2_500_000,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
    ],
]
let input = AVAssetWriterInput(mediaType: .video, outputSettings: videoSettings)
input.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(
    assetWriterInput: input,
    sourcePixelBufferAttributes: [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
        kCVPixelBufferWidthKey as String: width,
        kCVPixelBufferHeightKey as String: height,
    ]
)
guard writer.canAdd(input) else { fail("Cannot add video input") }
writer.add(input)
guard writer.startWriting() else { fail("Video writer failed to start: \(writer.error?.localizedDescription ?? "unknown")") }
writer.startSession(atSourceTime: .zero)
guard let pool = adaptor.pixelBufferPool else { fail("Video pixel-buffer pool unavailable") }

var cursor = 0.0
for (index, segment) in segments.enumerated() {
    while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.01) }
    let frame = pixelBuffer(from: segment.imagePath, width: width, height: height, pool: pool)
    let time = CMTime(seconds: cursor, preferredTimescale: 600)
    guard adaptor.append(frame, withPresentationTime: time) else { fail("Failed to append slide \(index + 1)") }
    cursor += durations[index]
}

while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.01) }
let finalFrame = pixelBuffer(from: segments.last!.imagePath, width: width, height: height, pool: pool)
let finalTime = CMTime(seconds: max(0, totalDuration - (1.0 / 30.0)), preferredTimescale: 600)
guard adaptor.append(finalFrame, withPresentationTime: finalTime) else { fail("Failed to append final frame") }
input.markAsFinished()
writer.endSession(atSourceTime: CMTime(seconds: totalDuration, preferredTimescale: 600))
let writerDone = DispatchSemaphore(value: 0)
writer.finishWriting { writerDone.signal() }
writerDone.wait()
guard writer.status == .completed else { fail("Video writing failed: \(writer.error?.localizedDescription ?? "unknown")") }

let composition = AVMutableComposition()
let videoAsset = AVURLAsset(url: tempVideoURL)
guard let sourceVideoTrack = videoAsset.tracks(withMediaType: .video).first,
      let targetVideoTrack = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid)
else { fail("Could not create video composition track") }
try targetVideoTrack.insertTimeRange(CMTimeRange(start: .zero, duration: videoAsset.duration), of: sourceVideoTrack, at: .zero)

guard let targetAudioTrack = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)
else { fail("Could not create audio composition track") }
var audioCursor = CMTime.zero
for segment in segments {
    let audioAsset = AVURLAsset(url: URL(fileURLWithPath: segment.audioPath))
    guard let sourceAudioTrack = audioAsset.tracks(withMediaType: .audio).first else { fail("Missing audio track: \(segment.audioPath)") }
    try targetAudioTrack.insertTimeRange(CMTimeRange(start: .zero, duration: audioAsset.duration), of: sourceAudioTrack, at: audioCursor)
    audioCursor = CMTimeAdd(audioCursor, audioAsset.duration)
}

guard let exporter = AVAssetExportSession(asset: composition, presetName: AVAssetExportPresetHighestQuality) else {
    fail("Could not create video exporter")
}
exporter.outputURL = outputURL
exporter.outputFileType = .mp4
exporter.shouldOptimizeForNetworkUse = true
let exportDone = DispatchSemaphore(value: 0)
exporter.exportAsynchronously { exportDone.signal() }
exportDone.wait()
guard exporter.status == .completed else { fail("Video export failed: \(exporter.error?.localizedDescription ?? "unknown")") }

try? FileManager.default.removeItem(at: tempVideoURL)
print(String(format: "Created %.2f-second video with %d slides", totalDuration, segments.count))
