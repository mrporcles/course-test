## What you'll get out of this lesson

This lesson walks through a hands-on lab that puts the "Configure Tests using Spring Profiles and working with Databases" lesson's profile and database-testing techniques into practice, on top of the Spring TestContext Framework annotations from the earlier testing lessons. By the end, you should be able to:

- Replace a hand-written `setUp`/`tearDown` test lifecycle with `@SpringJUnitConfig`
- Diagnose and fix a `NoUniqueBeanDefinitionException` caused by two competing bean implementations
- Use `@Profile` and `@ActiveProfiles` together to pick which implementation gets wired into a test
- Embed a test's configuration as a static inner class instead of pointing at an external configuration class

## The starting point

In every previous lab, the application context was created programmatically inside a `setUp` method. This lab (project 24) asks a simple question: is there a better way to do it? The answer is the Spring TestContext Framework already covered earlier in this module, now combined with profiles for a more dynamic test configuration. The lab is organized as a series of numbered to-dos, and this lesson follows that same order.

## To-do 1: Replacing manual setup with `@SpringJUnitConfig`

The starting test class has a `@BeforeEach` method that builds the application context and grabs a reference to the `RewardNetwork` bean, plus an `@AfterEach` method that closes the context afterward. The first to-do replaces all of that:

1. Annotate the class with `@SpringJUnitConfig`, pointing it at `TestInfrastructureConfig` — the same configuration class the manual setup was already using.
2. Delete the `@BeforeEach` and `@AfterEach` methods entirely, along with the field holding the application context — none of it is needed anymore.

Running the test at this point is expected to fail, and it does: a red bar, caused by a `NullPointerException` when the test tries to use `rewardNetwork`.

![Test failing with a NullPointerException before @Autowired is added](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/08-testing/05-lab-demo/images/lesson32-test-failure-before-autowired.png)

The reason is straightforward: the application context is now being created automatically, but nothing is injecting `rewardNetwork` into the test. The fix is to annotate the field with `@Autowired`. Once that's in place and the test reruns, it passes — the context is created, `RewardNetwork` is retrieved from it, and it's made available inside the test automatically.

## To-do 2: Annotating stub repositories with `@Repository`

The project has stub repository classes (used as fakes) living in `rewards.internal`. This to-do annotates all three of them — `StubAccountRepository`, `StubRestaurantRepository`, and `StubRewardRepository` — with `@Repository`, without assigning any profile yet, simply to make them Spring-managed beans that are part of the application context.

Running the test now is expected to fail again, and this to-do asks you to understand exactly why. The failure this time is a `NoUniqueBeanDefinitionException`:

![NoUniqueBeanDefinitionException: two matching beans found for AccountRepository](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/08-testing/05-lab-demo/images/lesson32-ambiguous-bean-error.png)

```
No qualifying bean of type 'rewards.internal.account.AccountRepository' available:
expected single matching bean but found 2: stubAccountRepository, jdbcAccountRepository
```

Component scanning is now picking up *both* the existing JDBC repository implementations and the newly-annotated stub implementations. Both get registered in the application context, and when something needs an `AccountRepository` injected, Spring has no way to know which of the two beans to choose — an ambiguity error.

## To-do 3: Disambiguating with `@Profile`

The fix is to put the JDBC and stub implementations into two different profiles, so only one set is active at a time:

- Annotate each JDBC repository implementation (`JdbcAccountRepository`, `JdbcRestaurantRepository`, `JdbcRewardRepository`) with `@Profile("jdbc")`.
- Annotate each stub repository implementation (`StubAccountRepository`, `StubRestaurantRepository`, `StubRewardRepository`) with `@Profile("stub")`.

With that done, the next step is to activate the `stub` profile inside the test using `@ActiveProfiles("stub")`. Recall from the "Configure Tests using Spring Profiles and working with Databases" lesson that `@SpringJUnitConfig` still builds the application context — `@ActiveProfiles` now tells it which profile-tagged beans to include alongside it.

Running the test after this change should no longer hit the ambiguity error, since only the stub implementations are active. Checking the log confirms it: the stub reward repository, stub restaurant repository, and stub account repository are all created — and the JDBC implementations are skipped entirely. The test passes with a green bar.

## To-do 4: Switching to the `jdbc` profile

Changing `@ActiveProfiles` from `"stub"` to `"jdbc"` swaps which set of repositories gets initialized. Rerunning the test and checking the log confirms the JDBC implementations are used this time instead of the stubs — and the test still passes, proving the profile-based switch works cleanly in both directions.

## To-do 5: Assigning the `local` profile

`TestInfrastructureLocalConfig` — a configuration class holding a local `DataSource` bean — gets annotated with `@Profile("local")` at the class level. As covered in the "Configure Tests using Spring Profiles and working with Databases" lesson, annotating the whole configuration class with `@Profile` makes every bean defined inside it belong to that profile, which is simpler here than annotating each `@Bean` method individually.

## To-do 6: Activating `jdbc` and `local` together

Since the test now needs more than one profile active at once, `@ActiveProfiles` takes an array of strings instead of a single value: `@ActiveProfiles({"jdbc", "local"})`. Before this to-do, the local `DataSource` bean belonged to no profile, so it was always initialized by default; now that it's tied to the `local` profile, it only gets created because that profile is explicitly activated. Running the test confirms everything still passes with both profiles active.

## To-do 7: Switching from `local` to `jndi`

A second configuration class, `TestInfrastructureJndiConfig`, defines its own `DataSource`, with everything inside it belonging to the `jndi` profile. Swapping `@ActiveProfiles` from `{"jdbc", "local"}` to `{"jdbc", "jndi"}` and rerunning the test switches which `DataSource` gets used — the log shows a simulated JNDI lookup happening instead of the local data source setup, and the test still comes back green.

## To-do 8 (optional): Embedding the configuration as a static inner class

The last to-do experiments with a different way of supplying `@SpringJUnitConfig`'s configuration. Instead of pointing at the external `TestInfrastructureConfig` class (which in turn imports the local, JNDI, and reward configuration classes), the same configuration is recreated as a `static` inner class directly inside the test class.

![Final test class with @SpringJUnitConfig, @ActiveProfiles("stub"), and the project's profile-based repositories](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/08-testing/05-lab-demo/images/lesson32-activeprofiles-stub-test-class.png)

When `@SpringJUnitConfig` is given no explicit `classes` attribute, the TestContext Framework looks for a static inner configuration class inside the test class itself and uses that as the entry point instead. Once the inner class is in place and the external reference is removed, rerunning the test produces the same green bar as before, using the same active profiles — confirming the two approaches are functionally equivalent.

## Recap

- The Spring TestContext Framework (`@SpringJUnitConfig`) replaces hand-written `@BeforeEach`/`@AfterEach` application-context setup, but the test still needs `@Autowired` to actually get its dependencies injected.
- Annotating two competing repository implementations with the same stereotype annotation, without profiles, produces a `NoUniqueBeanDefinitionException` — Spring can't decide which bean to inject.
- `@Profile` on each implementation, combined with `@ActiveProfiles` on the test class, resolves the ambiguity by only activating one implementation set at a time.
- `@ActiveProfiles` accepts an array of profile names when more than one profile needs to be active simultaneously.
- `@SpringJUnitConfig` can load its configuration from an external class or from a `static` inner class defined directly inside the test — both work identically.

## Check your understanding

1. Why did the test fail with a `NullPointerException` immediately after switching to `@SpringJUnitConfig`, before `@Autowired` was added?
2. What specifically caused the `NoUniqueBeanDefinitionException` in to-do 2, and which annotation combination fixed it in to-do 3?
3. How does `@SpringJUnitConfig` know to use a static inner class as its configuration source instead of an external class?

The next lesson moves into a new module, starting with the problems plain JDBC code has and how Spring's `JdbcTemplate` fixes them.
