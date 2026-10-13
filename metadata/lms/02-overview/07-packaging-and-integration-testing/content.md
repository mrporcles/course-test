## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain what a "fat" (or "Uber") JAR is and why Spring Boot's tooling builds one
- Use the Spring Boot Maven plugin to package and run an application
- Explain the difference between the two JAR files produced by `mvn package`
- Use `@SpringBootTest` to bootstrap an application context in a test, and explain how it auto-discovers its configuration

## Packaging your application

Spring Boot offers a few different options for packaging an application: as a JAR file, as a WAR file, or even as a container image — the latest versions of Spring Boot can build an OCI container image directly from your application, ready to deploy to a platform like Kubernetes.

This lesson focuses on JAR packaging specifically. The JAR you build is called an **Uber JAR** (or "fat" JAR), because it contains every library your application depends on, not just your own compiled code.

- A fat JAR contains all dependencies, including an embedded server container (Tomcat, Undertow, or Jetty) for a web application
- Because everything it needs is bundled in, it can be run directly with `java -jar`
- To create one, add the Spring Boot plugin to your Maven POM or Gradle build file, then build in the usual way — `gradle assemble` or `mvn package`

Building the JAR produces **two** files, not one:

- `my-app.jar` — the executable "fat" JAR
- `my-app.jar.original` — the "usual" JAR, containing just your own compiled classes

## The Spring Boot Maven plugin

In Maven, this is enabled by declaring the `spring-boot-maven-plugin`:

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

This plugin does two things: it extends the `package` goal so that `mvn package` produces the fat JAR, and it adds a `spring-boot:run` goal, letting you run the application directly with `mvn spring-boot:run` without packaging it first.

## What `mvn package` actually produces

Running `mvn package` and looking in the `target` directory shows the size difference between the two JARs clearly:

```
22M  yourapp-0.0.1-SNAPSHOT.jar
 5K  yourapp-0.0.1-SNAPSHOT.jar.original
```

- `.jar.original` contains only your code — a traditional JAR file
- `.jar` contains your code **and** all dependencies, and is executable — notice how much bigger it is

You'll use the larger, self-contained JAR to actually run the application with `java -jar`.

## Integration testing with \@SpringBootTest

Earlier in the course you saw how to bootstrap an application context in a test environment using `@SpringJUnitConfig`. That annotation picks a set of configuration classes and builds a context from them — but it doesn't apply any auto-configuration.

Swapping the annotation for `@SpringBootTest` changes that:

![Test: @SpringBootTest](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/02-overview/07-packaging-and-integration-testing/images/lesson6-springboottest-example.png)

```java
@SpringBootTest(classes = Application.class)
public class TransferServiceTests {

    @Autowired
    private TransferService transferService;

    @Test
    public void successfulTransfer() {
        TransferConfirmation conf = transferService.transfer(...);
        ...
    }
}
```

`@SpringBootTest`'s `classes` attribute points at your entry point — here, a class annotated with `@SpringBootApplication`. Because `@SpringBootApplication` enables auto-configuration, the application context built for this test is created the *same way* a real Spring Boot application would build it: the same auto-configuration, the same `application.properties`, everything. In terms of how you actually write the test, nothing else changes — you autowire beans from the context and use them exactly as before. The only thing that changed is the annotation controlling how that context gets built.

## Letting \@SpringBootTest find its own configuration

You can safely omit `classes` entirely from `@SpringBootTest`, because it's able to auto-discover your entry point:

```java
@SpringBootTest  // classes not needed
public class TransferServiceTests {
    // same tests as previous slide
}
```

```java
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan("transfers")
public class Application {
    // Bean methods
}
```

Here's how that discovery works: `@SpringBootTest` walks up the package hierarchy looking for a class annotated with `@SpringBootConfiguration`, provided that configuration lives in a package *above* the test. Recall that a class annotated with `@SpringBootApplication` is, among other things, annotated with `@SpringBootConfiguration` — it's a configuration class that also performs component scanning and enables auto-configuration. Since a project usually has exactly one such class (its entry point), `@SpringBootTest` can reliably find it on its own. Only one `@SpringBootConfiguration`-annotated class is allowed in any given hierarchy, which is what makes this auto-discovery unambiguous.

Next up is the **module quiz**, where you can test your understanding of what you have covered in this module.
