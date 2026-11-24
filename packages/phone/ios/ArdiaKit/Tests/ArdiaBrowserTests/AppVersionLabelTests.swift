import ArdiaBrowser
import Testing

struct AppVersionLabelTests {
  private let testFlight = AppVersionLabel.testFlightReceiptName

  @Test func `a debug build is Dev whatever it was built as`() {
    #expect(AppVersionLabel.text(releaseVersion: "0.2.47", build: "12", isDebug: true, receiptName: nil) == "Solstice Dev (12)")
    #expect(AppVersionLabel.text(releaseVersion: "0.2.47-nightly.2", build: "12", isDebug: true, receiptName: testFlight) == "Solstice Dev (12)")
  }

  @Test func `a build without a release version is Dev`() {
    #expect(AppVersionLabel.text(releaseVersion: "", build: "3", isDebug: false, receiptName: "receipt") == "Solstice Dev (3)")
    #expect(AppVersionLabel.text(releaseVersion: "", build: "3", isDebug: false, receiptName: testFlight) == "Solstice Dev (3)")
    #expect(AppVersionLabel.text(releaseVersion: "1.0", build: "3", isDebug: false, receiptName: testFlight) == "Solstice Dev (3)")
    #expect(AppVersionLabel.text(releaseVersion: "0.2.47-beta.1", build: "3", isDebug: false, receiptName: testFlight) == "Solstice Dev (3)")
  }

  @Test func `TestFlight is Nightly, numbered for a nightly release`() {
    #expect(AppVersionLabel.text(releaseVersion: "0.2.47-nightly.2", build: "40", isDebug: false, receiptName: testFlight) == "Solstice 0.2.47 Nightly 2 (40)")
    #expect(AppVersionLabel.text(releaseVersion: "0.2.47", build: "41", isDebug: false, receiptName: testFlight) == "Solstice 0.2.47 Nightly (41)")
  }

  @Test func `the App Store is Stable`() {
    #expect(AppVersionLabel.text(releaseVersion: "0.2.47", build: "41", isDebug: false, receiptName: "receipt") == "Solstice 0.2.47 (41)")
    #expect(AppVersionLabel.text(releaseVersion: "0.2.47-nightly.2", build: "40", isDebug: false, receiptName: "receipt") == "Solstice 0.2.47 (40)")
    #expect(AppVersionLabel.text(releaseVersion: "0.2.47", build: "41", isDebug: false, receiptName: nil) == "Solstice 0.2.47 (41)")
  }
}
