## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain why testing should be a routine part of your development cycle, not an afterthought
- Describe the three components JUnit 5 is split into, and what each one is responsible for
- Map the JUnit 4 annotations you may already know onto their JUnit 5 replacements
- Recognize JUnit 5's new annotations, and know which package they need to be imported from

## Why this module exists

Testing is essential to guarantee that your application is working as expected, and it should be part of your regular development cycle rather than something bolted on at the end. This module is about testing Spring applications specifically: by the time it's done, you should be able to use JUnit 5 together with Spring so you can bootstrap the application context inside a test environment and use your real components directly inside test methods.

The module starts with a quick introduction to JUnit 5 itself (this lesson), then moves into integration testing with Spring (the "Write Integration Tests using Spring" lesson) — bootstrapping the application context inside a test environment — before going further into testing with profiles and testing with databases in later lessons.

## JUnit 5: three components instead of one jar

JUnit 5 is the testing framework used throughout the labs in this course, and it's fully supported by both Spring and Spring Boot. JUnit 5 support is a major feature of Spring 5.3, and JUnit 5 is the default JUnit version from Spring Boot 2.6. It requires Java 8+ at runtime and leverages Java 8 features, so lambdas are fair game inside your test methods.

JUnit 4 was a monolith — a single jar file containing everything. JUnit 5 was rewritten from scratch with a clean separation of concerns, split across three components:

- **JUnit Platform** — the engine responsible for actually running your tests.
- **JUnit Jupiter** — the API you write your tests against. ("Jupiter" is the fifth planet from the sun — a nod to this being JUnit *5*.)
- **JUnit Vintage** — a compatibility layer that lets you run existing JUnit 3 and JUnit 4 tests on top of the JUnit 5 platform, so older tests don't need to be rewritten just to keep running.

## Mapping JUnit 4 annotations to JUnit 5

Several JUnit 4 annotations have direct JUnit 5 replacements — same idea, new name and new package:

| JUnit 4 | JUnit 5 |
|---|---|
| `@Before` | `@BeforeEach` |
| `@BeforeClass` | `@BeforeAll` |
| `@After` | `@AfterEach` |
| `@AfterClass` | `@AfterAll` |
| `@Ignore` | `@Disabled` |

`@BeforeEach` runs before every single test method (the old `@Before`); `@BeforeAll` runs once before all the test methods in a class (the old `@BeforeClass`) — and the `@After...` variants mirror the same pattern on the way out.

JUnit 5 also introduces genuinely new annotations that didn't have a JUnit 4 equivalent at all: `@DisplayName`, `@Nested`, and `@ParameterizedTest`, among others.

**One important gotcha:** JUnit 5 completely ignores JUnit 4 annotations — it's easy to accidentally mix and match imports from `org.junit` (JUnit 4) and `org.junit.jupiter` (JUnit 5), and the code will often still compile, but the JUnit 4 annotations will simply be silently ignored. Always double-check that your imports come from the Jupiter package.

## A first JUnit 5 test

```java
import static org.junit.jupiter.api.Assertions.fail;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

class StandardTests {

    @BeforeAll
    static void initAll() { ... }       // Replaces @BeforeClass

    @BeforeEach
    void init() { ... }                 // Replaces @Before

    @Test
    void succeedingTest() { }

    @Test
    void failingTest() {
        fail("a failing test");
    }

    @Test
    @Disabled("for demo purposes")      // Replaces @Ignore
    void skippedTest() {
        // not executed
    }
}
```

Every import comes from `org.junit.jupiter` — that's the detail to watch for. `@BeforeAll` replaces `@BeforeClass`, `@BeforeEach` replaces `@Before`, `@Disabled` replaces `@Ignore`, and `@Test` itself hasn't changed its name at all, just its package — which is exactly the kind of subtle mismatch that causes the mixed-imports gotcha above. Make sure you're always importing `@Test` from `org.junit.jupiter.api`, not the old `org.junit` package.

Now that JUnit 5 itself is covered, the next lesson puts it together with Spring to write real integration tests.
