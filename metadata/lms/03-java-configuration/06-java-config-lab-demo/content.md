## What you'll get out of this lesson

This lesson walks through a hands-on lab that puts the Java configuration lessons into practice: writing configuration classes, defining beans, wiring dependency injection between them, and testing the result. By the end, you should be able to:

- See how Spring fits into the architecture of a typical enterprise Java application
- Write `@Configuration` classes and `@Bean` methods from scratch, rather than just reading them on a slide
- Use constructor injection to pass a `DataSource` into a configuration class, and method invocation to wire beans together
- Bootstrap an application context in a JUnit 5 test and use it to prove the whole configuration works end-to-end

## The scenario

This lab uses project **12, "Java config dependency injection,"** which is built around the same "reward dining" application introduced in the previous lab. The reward network needs three repositories — for accounts, restaurants, and rewards — plus a `DataSource` for them to talk to. The job of this lab is to configure all of that using plain Java-based configuration, and then prove it works with a test that bootstraps a real application context.

The lab instructions are organized as a series of numbered to-dos, and the walkthrough below follows that same order.

## To-do 0: read the brief

To-do 0 always just states what the lab is about: in this case, creating configuration classes, defining beans, wiring up dependency injection between them, and finishing with a test that verifies everything works as expected.

## To-do 1: make the class a configuration class

The starting class isn't a configuration class yet — it's just a plain Java class. Recall from the "Quick Start with Java Configuration" lesson that a configuration class is simply a Java class annotated with `@Configuration`, telling Spring that it contains bean definitions. Adding that one annotation is the entire to-do; there are no bean definitions inside it yet, but it's now recognized as a configuration class.

## To-do 2: define the bean methods

Next, four components need bean definitions: the reward network, the account repository, the restaurant repository, and the reward repository. That means writing four methods, each annotated with `@Bean`, one per component — using the *interface* type as the return type for each, rather than a concrete implementation class. At this point the methods are still empty; they'll be filled in during the next to-do.

## To-do 3: inject the `DataSource` through the constructor

The repositories created in to-do 2 all need a `DataSource`. Following the separation-of-concerns principle from the "Handling Multiple Configurations" lesson, the data source itself isn't configured in this class — it lives in a separate infrastructure configuration class — but this class still needs access to it.

The fix is constructor injection: add a constructor that accepts a `DataSource` and stores it in a private field.

```java
@Configuration
public class RewardsConfig {

    private final DataSource dataSource;

    public RewardsConfig(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    // ... bean methods go here
}
```

Worth noting: when a class has a single constructor, Spring doesn't require the `@Autowired` annotation on it — Spring discovers and uses that constructor automatically. It's fine to add `@Autowired` anyway for extra clarity, but it isn't required here, so the lab omits it and lets Spring find the constructor on its own.

## To-do 4: implement the bean methods

![RewardsConfig with @Bean methods being implemented](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/03-java-configuration/06-java-config-lab-demo/images/lesson11-rewardsconfig-bean-methods.png)

Now the bean methods from to-do 2 get real bodies. Looking at the actual repository implementation classes (inside `rewards.internal`, under the account and restaurant repository packages), each one exposes a `setDataSource` setter method that needs to be called to wire in the data source:

```java
@Bean
public AccountRepository accountRepository() {
    JdbcAccountRepository repo = new JdbcAccountRepository();
    repo.setDataSource(dataSource);
    return repo;
}

@Bean
public RestaurantRepository restaurantRepository() {
    JdbcRestaurantRepository repo = new JdbcRestaurantRepository();
    repo.setDataSource(dataSource);
    return repo;
}

@Bean
public RewardRepository rewardRepository() {
    JdbcRewardRepository repo = new JdbcRewardRepository();
    repo.setDataSource(dataSource);
    return repo;
}
```

With the three repositories in place, the reward network itself can be created. Its implementation class has a constructor that accepts all three repositories, so the bean method uses method invocation to supply them:

```java
@Bean
public RewardNetwork rewardNetwork() {
    return new RewardNetworkImpl(
        accountRepository(),
        restaurantRepository(),
        rewardRepository());
}
```

Calling `accountRepository()`, `restaurantRepository()`, and `rewardRepository()` directly, from inside another `@Bean` method, is exactly the method-invocation style of dependency injection seen in earlier lessons — Spring resolves those calls against the beans already registered in the context rather than actually re-running the methods from scratch.

## To-do 5: uncomment and run the first test

To-do 5 asks you to uncomment a block of test code and fix up the imports (a quick job for the IDE's "organize imports" shortcut). With the configuration from to-dos 1–4 in place, running the test produces a green bar — the first proof that the configuration is wired correctly.

## To-do 6: study the provided `TestInfrastructureConfig`

A new configuration class, `TestInfrastructureConfig`, is provided for you rather than written from scratch. It contains a single bean of type `DataSource` that creates and populates an in-memory HSQLDB database, using SQL scripts pulled from a shared "rewards common" project (specifically, `rewards/testdb` under that project's resources, containing `schema.sql` and `data.sql`). This to-do is just about reading and understanding that class — it's the infrastructure half of the separation-of-concerns split from the "Handling Multiple Configurations" lesson.

## To-do 7: import the application configuration

The application configuration (`RewardsConfig`, from to-dos 1–4) needs to become part of the same context as the test infrastructure config, since together they'll form the entry point passed to `SpringApplication.run`. That's done with `@Import`:

```java
@Configuration
@Import(RewardsConfig.class)
public class TestInfrastructureConfig {
    @Bean
    public DataSource dataSource() {
        // builds and populates an embedded HSQLDB
    }
}
```

Passing `TestInfrastructureConfig` to the application context now brings along every bean from `RewardsConfig` as well.

## To-do 8: create the JUnit 5 test class

Next, a new test class called `RewardNetworkTests` gets created in the same package as `TestInfrastructureConfig`, using the IDE's "New JUnit Test Case" wizard (selecting the JUnit 5 option), including a generated setup method.

## To-do 9: bootstrap the context in `setUp`

The generated `setUp` method — annotated `@BeforeEach`, exactly as in the "The Application Context" lesson — is where the application context gets created:

```java
private RewardNetwork rewardNetwork;

@BeforeEach
public void setUp() {
    ApplicationContext context =
        SpringApplication.run(TestInfrastructureConfig.class);
    rewardNetwork = context.getBean(RewardNetwork.class);
}
```

Passing `TestInfrastructureConfig` — the class carrying the `@Import` from to-do 7 — means the resulting context includes both the test data source *and* every application bean pulled in from `RewardsConfig`. Since there's only one bean of type `RewardNetwork` in that context, `getBean(RewardNetwork.class)` can look it up by type alone, no bean name required.

## To-do 10: run a placeholder test

The next to-do checks that a test method exists, renames it to `testRewardForDining`, strips out any body, and runs it. Even with an empty body, running it still has to bootstrap the entire application context — so a green bar here already confirms the configuration itself is correct, before any real assertions are added.

## To-do 11: fill in the real test logic

![RewardNetworkImplTests with the copied test logic, passing](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/03-java-configuration/06-java-config-lab-demo/images/lesson11-rewardnetwork-test-passing.png)

The final to-do points to an existing class, `RewardNetworkImplTests`, which tests the same reward network logic but *without* Spring — it manually creates stub repositories and constructs the reward network by hand. The job here is to copy that test's logic into the new Spring-backed test class.

Running the completed test produces a green bar, which confirms something meaningful: the reward network is genuinely delegating to the repositories configured in to-do 4, and those repositories are pulling real data out of the data source configured in to-do 6 — the whole chain, from application context down to the embedded database, works correctly.

With the fundamentals of Java-based configuration now practiced hands-on, the module quiz is next, where you can check your understanding of what you have learned. The next module then covers externalizing properties, profiles, and SpEL.
