import AppKit
import AVFoundation
import Foundation

struct Segment: Decodable {
    let id: String
    let title: String
    let textPath: String
    let audioPath: String
    let imagePath: String
}

let root = "/Users/ruby/Projects/active-radar-tracker-basics"
let videoURL = URL(fileURLWithPath: "\(root)/beginner/ai_audio/00-radar-intuition-presentation-video.mp4")
let manifestURL = URL(fileURLWithPath: "\(root)/.codex_tmp/00-radar-video/segments.json")
let checkDir = URL(fileURLWithPath: "\(root)/.codex_tmp/00-radar-video/video-check")
try FileManager.default.createDirectory(at: checkDir, withIntermediateDirectories: true)
let segments = try JSONDecoder().decode([Segment].self, from: Data(contentsOf: manifestURL))
let asset = AVURLAsset(url: videoURL)
print(String(format: "duration=%.3f", CMTimeGetSeconds(asset.duration)))
print("videoTracks=\(asset.tracks(withMediaType: .video).count)")
print("audioTracks=\(asset.tracks(withMediaType: .audio).count)")

let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true
generator.requestedTimeToleranceBefore = .zero
generator.requestedTimeToleranceAfter = .zero
var cursor = 0.0
for segment in segments {
    let audioAsset = AVURLAsset(url: URL(fileURLWithPath: segment.audioPath))
    let duration = CMTimeGetSeconds(audioAsset.duration)
    let sampleTime = CMTime(seconds: cursor + min(1.0, duration / 2.0), preferredTimescale: 600)
    var actual = CMTime.zero
    let image = try generator.copyCGImage(at: sampleTime, actualTime: &actual)
    let rep = NSBitmapImageRep(cgImage: image)
    let png = rep.representation(using: .png, properties: [:])!
    try png.write(to: checkDir.appendingPathComponent("slide-\(segment.id).png"))
    print(String(format: "slide-%@ start=%.3f duration=%.3f frame=%.3f", segment.id, cursor, duration, CMTimeGetSeconds(actual)))
    cursor += duration
}
