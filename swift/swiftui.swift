// SwiftUI + Combine framework idioms: View protocol, @State / @Binding /
// @ObservedObject / @EnvironmentObject / @Published property wrappers,
// @ViewBuilder result builder, Combine publishers, async/await in Task.
//
// Imports mirror real projects; they do not need to resolve for static
// analysis of View + property-wrapper + modifier shapes.
import SwiftUI
import Combine

// --- ObservableObject view model with @Published ---
final class UserViewModel: ObservableObject {
    @Published var users: [SwiftUser] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    private var cancellables = Set<AnyCancellable>()
    private let service: UserService

    init(service: UserService = UserService()) {
        self.service = service
    }

    func load() {
        isLoading = true
        service.fetchUsers()
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let err) = completion {
                        self?.errorMessage = err.localizedDescription
                    }
                },
                receiveValue: { [weak self] users in
                    self?.users = users
                }
            )
            .store(in: &cancellables)
    }

    @MainActor
    func loadAsync() async {
        isLoading = true
        defer { isLoading = false }
        do {
            users = try await service.fetchUsersAsync()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

struct SwiftUser: Identifiable, Codable {
    let id: Int
    let email: String
    let name: String?
}

final class UserService {
    func fetchUsers() -> AnyPublisher<[SwiftUser], Error> {
        let url = URL(string: "https://example.com/api/users")!
        return URLSession.shared.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: [SwiftUser].self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }

    func fetchUsersAsync() async throws -> [SwiftUser] {
        let url = URL(string: "https://example.com/api/users")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([SwiftUser].self, from: data)
    }
}

// --- SwiftUI view hierarchy ---
struct UsersListView: View {
    @StateObject private var viewModel = UserViewModel()
    @State private var searchText: String = ""
    @EnvironmentObject var settings: AppSettings

    var body: some View {
        NavigationStack {
            content
                .navigationTitle("Users")
                .searchable(text: $searchText)
                .toolbar {
                    ToolbarItem(placement: .primaryAction) {
                        Button("Refresh") {
                            Task { await viewModel.loadAsync() }
                        }
                    }
                }
                .onAppear { viewModel.load() }
        }
    }

    @ViewBuilder
    private var content: some View {
        if viewModel.isLoading {
            ProgressView()
        } else if let msg = viewModel.errorMessage {
            Text(msg).foregroundColor(.red)
        } else {
            List(filteredUsers) { user in
                NavigationLink(destination: UserDetailView(user: user)) {
                    UserRow(user: user)
                }
            }
        }
    }

    private var filteredUsers: [SwiftUser] {
        if searchText.isEmpty { return viewModel.users }
        return viewModel.users.filter { $0.email.localizedCaseInsensitiveContains(searchText) }
    }
}

struct UserRow: View {
    let user: SwiftUser
    var body: some View {
        VStack(alignment: .leading) {
            Text(user.name ?? "<anon>").font(.headline)
            Text(user.email).font(.subheadline).foregroundColor(.secondary)
        }
    }
}

struct UserDetailView: View {
    let user: SwiftUser
    @Binding var isFavorite: Bool

    init(user: SwiftUser, isFavorite: Binding<Bool> = .constant(false)) {
        self.user = user
        self._isFavorite = isFavorite
    }

    var body: some View {
        Form {
            Section("Profile") {
                LabeledContent("Email", value: user.email)
                LabeledContent("Name", value: user.name ?? "—")
            }
            Toggle("Favorite", isOn: $isFavorite)
        }
    }
}

final class AppSettings: ObservableObject {
    @Published var theme: String = "system"
}

@main
struct UsersApp: App {
    @StateObject private var settings = AppSettings()
    var body: some Scene {
        WindowGroup {
            UsersListView()
                .environmentObject(settings)
        }
    }
}
