// 1. Plain module import.
import Foundation

// 2. Specific declaration imports.
import func Foundation.abs
import struct Foundation.URL
import class Foundation.FileManager
import enum Foundation.ComparisonResult
import protocol Foundation.CustomStringConvertible

// 3. Submodule-form (Foundation.Process exists on macOS, shown as shape).
// import Foundation.Process      // shape-only; platform-gated

func importsDemo() {
    let a: Int = abs(-5)
    let url: URL? = URL(string: "https://example.com")
    let fm: FileManager = FileManager.default
    let c: ComparisonResult = .orderedAscending
    let _: CustomStringConvertible = url as Any as! CustomStringConvertible
    print("a=\(a) url=\(String(describing: url)) fm=\(fm) c=\(c)")
}
