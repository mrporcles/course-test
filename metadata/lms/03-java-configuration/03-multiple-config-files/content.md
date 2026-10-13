## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain why a single configuration file eventually becomes a liability as an application grows
- Use `@Import` to combine several `@Configuration` classes into a single application context
- Separate "application" configuration from "infrastructure" configuration, and explain why that separation matters
- Use constructor injection between configuration classes to share a bean like a `DataSource`
- Spot and fix the "tramp data" anti-pattern, where a dependency is passed through a bean method that doesn't actually need it

## Why split a configuration file at all

So far, every example has configured all of its beans in a single configuration file. That works fine for a small example, but real applications keep growing — and when they do, their configuration classes grow right along with them. A single class trying to hold every bean definition eventually becomes hard to read and hard to change safely.

This lesson focuses on splitting that configuration across multiple files, and then reassembling them into a single application context.

## Combining files with \@Import

![Creating an Application Context from Multiple Configurations](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/03-java-configuration/03-multiple-config-files/images/lesson9-import-multiple-configs.png)

Consider three configuration files:

- **`ApplicationConfig`** — everything related to the application itself: business logic, the service layer, the repository, and any other application-level component.
- **`WebConfig`** — everything related to the web layer: controllers and similar components.
- **`InfrastructureConfig`** — the infrastructure configuration, such as the data source.

```java
@Configuration
@Import({ApplicationConfig.class, WebConfig.class})
public class InfrastructureConfig {
    // ...
}
```

`InfrastructureConfig` is annotated with `@Configuration` like any other configuration class, but it's *also* annotated with `@Import`. This is the mechanism for combining multiple configuration files: `@Import` pulls in all the bean definitions from `ApplicationConfig` and from `WebConfig`, in addition to whatever `InfrastructureConfig` defines itself.

This combined class becomes your entry point: you pass *it* — not the individual pieces — to `SpringApplication.run` (the "The Application Context" lesson), and the beans sourced from all three files end up in one single application context.

## Separating application concerns from infrastructure concerns

Here's the problem with a single, mixed configuration file:

```java
@Configuration
public class ApplicationConfig {
    @Bean
    public TransferService transferService(AccountRepository repository)
    { return new TransferServiceImpl(repository); }

    @Bean
    public AccountRepository accountRepository(DataSource dataSource)
    { return new JdbcAccountRepository(dataSource); }

    @Bean
    public DataSource dataSource() {
        BasicDataSource dataSource = new BasicDataSource();
        dataSource.setDriverClassName("org.postgresql.Driver");
        dataSource.setUrl("jdbc:postgresql://localhost/transfer");
        dataSource.setUsername("transfer-app");
        dataSource.setPassword("secret45");
        return dataSource;
    }
}
```

Notice the coupling: the `transferService` and `accountRepository` beans are **application beans**, while `dataSource` is an **infrastructure bean** — and worse, it's a data source coupled directly to a local Postgres environment. If you want to switch databases, or simply run this application in a different environment, you have to go edit this same file that also contains your core business wiring.

That's exactly the kind of coupling worth avoiding. Infrastructure tends to change *between* environments — you'll have a different data source in testing than in production — while application code, the actual business logic, stays the same. So it's good practice to keep the two separated: the application code gets reused as-is, while only the infrastructure configuration changes underneath it.

## Partitioning the configuration

Splitting the example above gives you an `ApplicationConfig` containing only the application classes — the transfer service and the account repository — and a separate infrastructure configuration class per environment:

```java
@Configuration
public class ApplicationConfig {
    @Bean public TransferService transferService(AccountRepository repository) {
        return new TransferServiceImpl(repository);
    }

    @Bean public AccountRepository accountRepository(DataSource dataSource) {
        return new JdbcAccountRepository(dataSource);
    }
}

@Configuration
@Import(ApplicationConfig.class)
public class TestInfrastructureConfig {
    @Bean public DataSource dataSource() { ... }
}
```

`TestInfrastructureConfig` holds the data source for the test environment, and it imports `ApplicationConfig` to pull in the common application beans. If you wanted to run in production, you'd create a parallel `ProdInfrastructureConfig`, define its own production data source, and import `ApplicationConfig` the same way. The environment-specific class imports the shared, common configuration — you're reusing the same application logic in both cases, and only the infrastructure piece changes. Whichever infrastructure class you build, that becomes your entry point to `SpringApplication.run`.

## Sharing a bean across configuration files with constructor injection

Splitting your configuration into separate classes raises an obvious question: if the `DataSource` bean now lives in one file, how does another file get access to it?

The answer is: the same way any Spring bean gets a dependency — through injection, this time at the configuration-class level, using constructor injection.

```java
@Configuration
public class ApplicationConfig {
    private final DataSource dataSource;

    @Autowired
    public ApplicationConfig(DataSource ds) {
        this.dataSource = ds;
    }

    @Bean
    public AccountRepository accountRepository() {
        return new JdbcAccountRepository(dataSource);
    }
}

@Configuration
@Import(ApplicationConfig.class)
public class InfrastructureConfig {
    @Bean
    public DataSource dataSource() {
        DataSource ds = new BasicDataSource();
        // ...
        return ds;
    }
}
```

`InfrastructureConfig` defines the `DataSource` bean, and `ApplicationConfig` needs it. Because `ApplicationConfig` declares a constructor that accepts a `DataSource`, Spring simply injects it — the data source is configured in a different file, but since every configuration class ultimately contributes to the *same* application context, every bean can see every other bean regardless of which file defined it.

## A gotcha to avoid: "tramp data"

Splitting configuration across files means you sometimes have to be careful about *how* a dependency reaches the bean that actually needs it.

Consider a configuration class defining an `accountRepository` bean, which needs a `DataSource`:

```java
@Configuration
public class ApplicationConfig {
    @Bean public AccountRepository accountRepository(DataSource ds) {
        return new JdbcAccountRepository(ds);
    }
}
```

So far, so good — that's a legitimate dependency. But now look at what happens with an `accountService` bean that depends on the repository:

```java
@Configuration
public class ApplicationConfig {
    // Bad: dataSource is a "tramp"!
    @Bean public AccountService accountService(DataSource ds) {
        return new AccountService(accountRepository(ds));
    }

    @Bean public AccountRepository accountRepository(DataSource ds) {
        return new JdbcAccountRepository(ds);
    }
}
```

This *looks* plausible, but it isn't right: `accountService` accepts a `DataSource` argument purely so it can hand it down to a manual call to `accountRepository(ds)`. The data source isn't actually a dependency of the account service at all — it's just being ferried through, method call by method call, to satisfy something further down the chain. That pattern of passing a value through several layers, none of which actually need it for their own logic, is sometimes called **"tramp data,"** and it's a sign the configuration should be rethought.

The fix is to pass the *actual* dependency instead:

```java
@Configuration
public class ApplicationConfig {
    // Better: pass actual dependency
    @Bean public AccountService accountService(AccountRepository repo) {
        return new AccountService(repo);
    }

    @Bean public AccountRepository accountRepository(DataSource ds) {
        return new JdbcAccountRepository(ds);
    }
}
```

Now `accountService` simply declares a dependency on `AccountRepository` — which it actually needs — and Spring resolves that by calling the `accountRepository` bean method for you. No more forwarding an argument the calling bean has no real use for. If you ever find yourself passing a dependency into a bean method just so it can be relayed somewhere else, that's the signal to rethink the configuration, exactly like this.

With multiple configuration files in place, the next question is about how many instances of a given bean actually get created — which is exactly what the "Bean Scopes" lesson, on bean scopes, covers.
