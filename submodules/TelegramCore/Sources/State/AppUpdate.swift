import Foundation
import Postbox
import SwiftSignalKit
import MtProtoKit
import TelegramApi


public struct AppUpdateInfo: Equatable {
    public let blocking: Bool
    public let version: String
    public let text: String
    public let entities: [MessageTextEntity]
    
    public init(blocking: Bool, version: String, text: String, entities: [MessageTextEntity]) {
        self.blocking = blocking
        self.version = version
        self.text = text
        self.entities = entities
    }
}

extension AppUpdateInfo {
    init?(apiAppUpdate: Api.help.AppUpdate) {
        return nil
    }
}

func managedAppUpdateInfo(network: Network, stateManager: AccountStateManager) -> Signal<Never, NoError> {
    return .complete()
}
