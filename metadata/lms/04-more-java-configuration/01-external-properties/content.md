## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain why hard-coding property values in a configuration class is a bad practice
- Use Spring's `Environment` abstraction to read externalized property values
- Load a custom property file into the environment using `@PropertySource`
- Use `@Value` as a lighter-weight alternative to injecting the `Environment` directly

## Where this lesson is headed

Having covered the basics of Java configuration in the Java configuration lessons, this lesson takes a deeper look at three more capabilities:

1. **Externalizing properties** — passing values into your bean definitions without hard-coding them.
2. **Profiles** — grouping beans so different sets activate in different situations (covered in the "Spring Profiles" lesson).
3. **Spring Expression Language (SpEL)** — a short introduction (covered in the "Spring Expression Language (SpEL)" lesson).

This lesson covers the first of the three.

## The problem with hard-coded values

Recall the `DataSource` bean definition from earlier lessons:

```java
@Bean
public DataSource dataSource() {
    BasicDataSource ds = new BasicDataSource();
    ds.setDriverClassName("org.postgresql.Driver");
    ds.setUrl("jdbc:postgresql://localhost/transfer");
    ds.setUser("transfer-app");
    ds.setPassword("secret45");
    return ds;
}
```

Every value here — the driver, the URL, the username, the password — is hard-coded directly into the configuration file. That's a bad practice: if any of these values need to change, you have to edit the configuration file itself and recompile the application. That's not flexible, and it's definitely not ideal, especially for something as environment-sensitive as database credentials.

A better approach is to **externalize** these values — pull them out into something like a property file, so they can change without touching the compiled code at all.

## Spring's `Environment` abstraction

Spring provides the **`Environment`** abstraction specifically for this purpose: it represents properties loaded from the runtime environment, and it's the tool you'll use to read externalized values into your application.

Properties available through the `Environment` can come from several different sources, in this order:

1. JVM system properties — `System.getProperty()`
2. System environment variables — `System.getenv()`
3. Java properties files

### Refactoring the data source to use externalized values

Suppose the driver, URL, username, and password have been moved into a property file called `db.properties`, using keys like `db.driver`, `db.url`, `db.user`, and `db.password`:

```properties
db.driver=org.postgresql.Driver
db.url=jdbc:postgresql:localhost/transfer
db.user=transfer-app
db.password=secret45
```

To read those values back inside a configuration class, one option is to **inject the `Environment` bean directly**, exactly like any other Spring bean:

```java
@Configuration
public class DbConfig {

    @Bean
    public DataSource dataSource(Environment env) {
        BasicDataSource ds = new BasicDataSource();
        ds.setDriverClassName(env.getProperty("db.driver"));
        ds.setUrl(env.getProperty("db.url"));
        ds.setUser(env.getProperty("db.user"));
        ds.setPassword(env.getProperty("db.password"));
        return ds;
    }
}
```

The `Environment` is passed in as a method argument, and `getProperty(...)` fetches each value by key. Now, changing the connection details means editing `db.properties` — no recompiling, and no touching this configuration class at all.

## Telling Spring about your property file: \@PropertySource

Injecting the `Environment` only helps once Spring actually knows your property file exists. Environment variables and JVM system properties are always available automatically, but a custom property file has to be explicitly registered — this is called a **property source**.

You register one with the `@PropertySource` annotation:

```java
@Configuration
@PropertySource("classpath:/com/organization/config/app.properties")
@PropertySource("file:config/local.properties")
public class ApplicationConfig {
    // ...
}
```

`@PropertySource` supports three prefixes for locating a file:

- **`classpath:`** — loads the file from the classpath, typically somewhere under `src/main/resources`.
- **`file:`** — loads the file from the file system, using either a relative or an absolute path.
- **`http:`** — loads the file over HTTP.

Both property sources shown above get added to the environment, and once they are, any property inside either file becomes available through `env.getProperty(...)`, in addition to the environment variables and system properties that are already there automatically.

## A lighter alternative: \@Value

If you don't want to inject the `Environment` component directly, `@Value` gives you a more direct route to the same values — asking the environment for one specific value at the point where you need it.

```java
@Configuration
public class DbConfig {

    @Bean
    public DataSource dataSource(
            @Value("${db.driver}") String driver,
            @Value("${db.url}") String url,
            @Value("${db.user}") String user,
            @Value("${db.password}") String pwd) {

        BasicDataSource ds = new BasicDataSource();
        ds.setDriverClassName(driver);
        ds.setUrl(url);
        ds.setUser(user);
        ds.setPassword(pwd);
        return ds;
    }
}
```

The dollar-sign syntax, `${...}`, tells Spring to resolve that expression against the environment. Here, four plain `String` arguments are injected — `db.driver`, `db.url`, `db.user`, and `db.password` — with no explicit reference to the `Environment` object anywhere in the method signature. Spring resolves each one before the method is even called, and the method body is left to just use the plain string values as if they'd always been there.

Grouping related beans so that only some of them are active in a given environment is the natural next step — and that's exactly what Spring profiles, covered in the next lesson, are for.
