package mono.web;

// Spring / JPA framework idioms: DI, stereotype annotations, mapping
// annotations, JPA entity, repository interface, bean lifecycle.
//
// Imports intentionally mirror what the parser sees in real projects —
// they don't need to resolve for static analysis of annotation shapes.
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Repository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.util.List;
import java.util.Optional;

@Entity
@Table(name = "users")
class SpringUser {
    @Id
    @GeneratedValue
    private Long id;

    @Column(name = "email", nullable = false, unique = true)
    private String email;

    @Column(length = 128)
    private String name;

    public Long getId() { return id; }
    public String getEmail() { return email; }
    public String getName() { return name; }
}

@Repository
interface SpringUserRepository {
    Optional<SpringUser> findById(Long id);
    List<SpringUser> findAll();
    SpringUser save(SpringUser user);
}

@Service
class SpringUserService {
    private final SpringUserRepository repo;

    @Autowired
    public SpringUserService(SpringUserRepository repo) {
        this.repo = repo;
    }

    @Transactional(readOnly = true)
    public Optional<SpringUser> findUser(Long id) {
        return repo.findById(id);
    }

    @Transactional
    public SpringUser createUser(SpringUser u) {
        return repo.save(u);
    }
}

@RestController
@RequestMapping("/api/users")
class SpringUserController {
    private final SpringUserService service;

    @Value("${app.default-limit:10}")
    private int defaultLimit;

    public SpringUserController(SpringUserService service) {
        this.service = service;
    }

    @GetMapping("/{id}")
    public ResponseEntity<SpringUser> get(@PathVariable Long id) {
        return service.findUser(id)
            .map(ResponseEntity::ok)
            .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<SpringUser> create(
            @RequestBody SpringUser body,
            @RequestParam(defaultValue = "false") boolean notify) {
        SpringUser saved = service.createUser(body);
        return ResponseEntity.ok(saved);
    }
}

@Component
class SpringStartupBean {
    public void onStart() {
        System.out.println("spring bean started");
    }
}
