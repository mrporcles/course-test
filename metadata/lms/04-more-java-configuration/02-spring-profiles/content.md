## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain what a profile is, and what problem it solves
- Apply `@Profile` at both the configuration-class level and the individual `@Bean` method level
- Use the `!` (negation) operator to define a fallback configuration for when a profile is *not* active
- Activate one or more profiles at runtime, using either a system property or code
- Combine `@Profile` with `@PropertySource` so a property file only loads when its matching profile is active

## The problem profiles solve

Your application will typically need different configuration depending on the environment or the specific situation it's running in — a test configuration, a production configuration, and maybe others besides. The question this lesson answers is: is there a way to cleanly segregate configuration like that? **Profiles** are Spring's answer.

## What is a profile?

A profile is really just a name — think of it as a namespace, or a group. It lets you group bean definitions together so that they're only included in the application context under certain conditions.

![Profiles - Beans can be grouped into Profiles](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/04-more-java-configuration/02-spring-profiles/images/lesson13-profiles-grouped.png)

In the diagram above, some beans — like the transfer service and the account service — don't belong to any profile at all, so they're **always** initialized, regardless of anything else. Other beans, though, are configured inside a specific profile.

A profile can represent an **environment**: `dev`, `test`, `production`. In the diagram, the data source is configured separately inside both a `test` profile and a `production` profile — since you'd typically activate only one of those at a time, they're mutually exclusive in practice, and you end up with exactly one data source in the resulting application context.

A profile can also represent an **implementation choice** — for example, `jdbc` versus `jpa` — or a **deployment platform**, like `on-premise` versus `cloud`. In the diagram, the data access layer configured under `jpa` uses JPA repositories, while the layer under `jdbc` uses JDBC repositories directly; again, these would typically be mutually exclusive.

Importantly, when you create the application context, you're not limited to activating just one profile — you can activate more than one at the same time. You could, for instance, activate both `jpa` and `production`, or both `jdbc` and `testing`.

## Defining profiles

### At the class level

The simplest way to assign beans to a profile is to annotate the whole configuration class with `@Profile`:

```java
@Configuration
@Profile("embedded")
public class DevConfig {

    @Bean
    public DataSource dataSource() {
        EmbeddedDatabaseBuilder builder = new EmbeddedDatabaseBuilder();
        return builder.setName("testdb")
                .setType(EmbeddedDatabaseType.HSQL)
                .addScript("classpath:/testdb/schema.db")
                .addScript("classpath:/testdb/test-data.db").build();
    }
    // ...
}
```

Everything inside `DevConfig` now belongs to the `embedded` profile. Nothing in this configuration class will be used unless `embedded` is chosen as one of the active profiles. (H2 and Derby are also supported as embedded database types, alongside HSQL shown here.)

### At the \@Bean method level

For finer-grained control, you can move `@Profile` down to individual `@Bean` methods instead of the whole class:

```java
@Configuration
public class DataSourceConfig {

    @Bean(name = "dataSource")
    @Profile("embedded")
    public DataSource dataSourceForDev() {
        EmbeddedDatabaseBuilder builder = new EmbeddedDatabaseBuilder();
        return builder.setName("testdb") ...
    }

    @Bean(name = "dataSource")
    @Profile("!embedded")
    public DataSource dataSourceForProd() {
        BasicDataSource dataSource = new BasicDataSource();
        // ...
        return dataSource;
    }
}
```

A couple of details worth noticing here:

- **Explicit bean names override the method name.** Both methods are given the same explicit name, `dataSource`, via `@Bean(name = "dataSource")` — even though the method names themselves (`dataSourceForDev`, `dataSourceForProd`) differ. Because both profiles define the *same* bean name, only one of the two should ever be active at the same time; otherwise you'd end up with a naming conflict.
- **The `!` (negation) operator.** `@Profile("!embedded")` means "active when `embedded` is *not* one of the active profiles." This is a handy technique: rather than maintaining two profiles and remembering to activate one whenever you deactivate the other, you can express one configuration as the direct opposite of the other.

The same negation technique works with any profile name, not just `embedded`:

```java
@Configuration
@Profile("cloud")
public class DevConfig {
    // ... used if cloud is the active profile
}

@Configuration
@Profile("!cloud")
public class ProdConfig {
    // ... used if cloud is not an active profile
}
```

## Activating profiles at runtime

Defining which beans belong to which profile is only half the story — profiles also need to be **activated** at runtime, or none of the profile-scoped beans will be picked up at all.

There are a few ways to do this:

- **A system property via the command line:**

  ```
  -Dspring.profiles.active=embedded,jpa
  ```

  (Note that this activates both `embedded` and `jpa` at once — profiles are comma-separated, and, as mentioned earlier, more than one can be active simultaneously.)

- **A system property, set programmatically** — this has to happen *before* the application context is created, i.e. before calling `SpringApplication.run`:

  ```java
  System.setProperty("spring.profiles.active", "embedded,jpa");
  SpringApplication.run(AppConfig.class);
  ```

- **`@ActiveProfiles`** — this one is specific to the test environment only, and isn't a way to activate a profile in your actual running application. It will be covered in a later module — don't confuse it with the two general-purpose mechanisms above.

### Working through an example

Suppose you have three configuration classes: one with no `@Profile` at all, one annotated `@Profile("jpa")`, and one annotated `@Profile("jdbc")`. If you activate the system property `spring.profiles.active=jpa`, which configuration classes get picked up to build the application context?

The answer: the first and the second. The first always gets included, since it doesn't belong to any profile. The second gets included because `jpa` was explicitly activated. The third is skipped, because `jdbc` was never activated.

## Combining profiles with property sources

Recall `@PropertySource` from the "Use External Properties" lesson — the way to load a property file into the `Environment`. It can be combined directly with `@Profile`, so that a given property file is only loaded when a specific profile is active.

![Property Source selection](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/04-more-java-configuration/02-spring-profiles/images/lesson13-property-source-selection.png)

```java
@Configuration
@Profile("local")
@PropertySource("local.properties")
class DevConfig { ... }

@Configuration
@Profile("cloud")
@PropertySource("cloud.properties")
class ProdConfig { ... }
```

`DevConfig`'s beans — and its `local.properties` file — are only active if the `local` profile is activated. `ProdConfig`'s beans, and its `cloud.properties` file, are only active if `cloud` is activated. This gives you dynamic, profile-driven loading of property files, on top of the profile-driven loading of beans covered earlier in this lesson.

## Recap

- A **profile** is a named group of bean definitions; beans with no profile are always active, while profile-scoped beans are only included when their profile is activated.
- `@Profile` can be applied to a whole `@Configuration` class or to individual `@Bean` methods for finer control.
- The `!` operator lets you define one configuration as "active when this profile is *not* active" — handy for maintaining exactly two mutually exclusive alternatives.
- Profiles are activated at runtime, either via the `-Dspring.profiles.active=...` system property on the command line, or programmatically with `System.setProperty(...)` before the context is created. `@ActiveProfiles` is a separate, test-only mechanism.
- More than one profile can be active at the same time.
- `@PropertySource` can be combined with `@Profile` so a property file only loads when its matching profile is active.

## Check your understanding

1. If a bean is defined inside a class with no `@Profile` annotation at all, under what conditions is it included in the application context?
2. What does `@Profile("!cloud")` mean, and why is it useful alongside a class annotated `@Profile("cloud")`?
3. Name the two general-purpose ways to activate a profile at runtime, and explain why `@ActiveProfiles` isn't a third option for a production application.

The next lesson introduces the last of this module's three topics: the Spring Expression Language, or SpEL for short.
