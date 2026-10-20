// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "ForjaCore",
    platforms: [.iOS(.v16), .macOS(.v13)],
    products: [.library(name: "ForjaCore", targets: ["ForjaCore"])],
    targets: [
        .target(name: "ForjaCore"),
        .testTarget(name: "ForjaCoreTests", dependencies: ["ForjaCore"], resources: [.copy("Resources")]),
    ]
)
