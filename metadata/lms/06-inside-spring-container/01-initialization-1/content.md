## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Name the three phases of the Spring container lifecycle and what happens in each
- Break the initialization phase down into its two steps, and explain what "loading bean definitions" means before any bean is actually created
- Explain what a `BeanFactoryPostProcessor` is, when it runs, and why it operates on definitions rather than instances
- Recognize `PropertySourcesPlaceholderConfigurer` as a real, built-in example of this extension point

## The three phases of the container lifecycle

Everything you've learned so far about beans — configuration styles, dependency injection, stereotype annotations, `@PostConstruct`/`@PreDestroy` — has been about *what* Spring creates and *how* it wires things together. This lesson starts looking at *when*, by opening up the container's actual lifecycle.

![Container Lifecycle: Initialization, Usage, Destruction](images/lesson20-container-lifecycle.png)

The Spring bean container runs through three distinct phases:

- **Initialization** — Spring beans are created, and dependency injection occurs.
- **Usage** — beans are available for use in the application; this is where your business logic actually runs, and where you'll spend most of your time as a developer.
- **Destruction** — beans are released for garbage collection, when the application context closes.

This lesson (and the next) zooms into the initialization phase specifically, since it's the most complex of the three.

## Initialization, step A and step B

Initialization happens when you call `SpringApplication.run(...)`. By the time that call returns, you have a fully configured application context — but getting there involves two distinct steps:

![Bean Initialization Steps](images/lesson20-bean-initialization-steps.png)

- **Step A: Load & Process Bean Definitions** — gather all the information about what needs to exist in the application context. Nothing is actually created yet; this step only produces *definitions*, kept in memory.
- **Step B: Create and Initialize Beans** — for each bean, find or create its dependencies, instantiate it, perform setter injection, and run it through bean post-processors (which, along with initializers, are covered in the next lesson).

This lesson focuses on step A — the part where nothing has been instantiated yet, but Spring has already figured out everything it's going to need to build.

## Step A in detail: loading and processing bean definitions

Step A itself breaks down into two things happening in sequence:

1. **`@Configuration` classes are processed, and/or `@Component`-annotated classes are scanned for.** It doesn't matter whether the configuration came from Java config, annotations, or (historically) XML — Spring gathers the same kind of information regardless: the bean's type, its name, its dependencies, its scope, and everything else needed to eventually construct it.
2. **Bean definitions get added to a `BeanFactory`**, each indexed under its id and type.

An `ApplicationContext` — the object you get back from `SpringApplication.run(...)` — *is* a `BeanFactory`; it extends it. So this `BeanFactory` is effectively a map: bean ID to bean definition, nothing more. No instances exist yet at this point, only the definitions describing what should eventually be created.

![Load Bean Definitions: from AppConfig.java to the BeanFactory](images/lesson20-load-bean-definitions-example.png)

Concretely: given an `AppConfig.java` with `@Bean` methods for `transferService()` and `accountRepository()`, Spring parses both method definitions and stores an entry for each — `transferService` and `accountRepository` — inside the `BeanFactory`. If your configuration is split across multiple files or classes, every one of them gets parsed the same way, but all their definitions land in the very same `BeanFactory` — you still end up with exactly one application context, no matter how many configuration classes contributed to it.

## `BeanFactoryPostProcessor`: an extension point on the definitions themselves

Once every bean definition has been loaded, Spring gives you one more chance to modify those definitions before anything gets instantiated: the `BeanFactoryPostProcessor`.

The name reads literally backwards from what it does: it **post-processes the bean factory** — meaning the bean *definitions* held inside it — not bean instances. It's a functional interface with a single method:

```java
public interface BeanFactoryPostProcessor {
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory);
}
```

You're handed the entire `BeanFactory`, definitions and all, and can modify any of them — because at this stage, no instance exists yet for any bean, so there's nothing to break by rewriting a definition. Spring ships with several built-in implementations of this interface for things like reading properties and registering custom scopes, but you can also write your own.

### A real example: `PropertySourcesPlaceholderConfigurer`

The most common example of a `BeanFactoryPostProcessor` you've already been relying on without necessarily knowing it: `PropertySourcesPlaceholderConfigurer`. Recall `@Value` and `${...}` placeholder syntax from earlier lessons.

![BeanFactoryPostProcessor's most common example: resolving @Value placeholders](images/lesson20-beanfactorypostprocessor-common-example.png)

```java
@Configuration
@PropertySource("classpath:/config/app.properties")
public class ApplicationConfig {
    @Value("${max.retries}")
    int maxRetries;
    // ...
}
```

Something has to actually go look up `max.retries` in `app.properties` and substitute the real value (`3`, say) into that placeholder — and that "something" is `PropertySourcesPlaceholderConfigurer`, doing its work as a `BeanFactoryPostProcessor`.

### Writing your own

If you needed to, you could define your own `BeanFactoryPostProcessor` the same way you'd define any other bean:

```java
@Bean
public static BeanFactoryPostProcessor myConfigurer() {
    return new MyConfigurationCustomizer();
}

public class MyConfigurationCustomizer implements BeanFactoryPostProcessor {
    // Perform customization of the configuration, such as the placeholder syntax
}
```

There is exactly one requirement worth remembering here: the `@Bean` method **must be `static`**. `BeanFactoryPostProcessor` beans need to be initialized before every other bean in the application context, since their entire job is to modify definitions before anything else gets created from them — marking the factory method `static` is what makes that early initialization possible.

### When you don't need to define one yourself

In practice, you'll rarely need to register `PropertySourcesPlaceholderConfigurer` manually:

- Spring Boot sets it up for you automatically.
- Plain Spring, from version 4.3 onward, sets up a basic value-resolver for you automatically if no `PropertySourcesPlaceholderConfigurer` bean already exists.

You'd only need to configure one manually if you're still on Spring 4.2 or earlier, or if you specifically want to control how it works — for instance, to have it ignore system environment variables or system properties when resolving placeholders.

## Recap

- The container lifecycle has three phases: initialization (beans created, dependencies injected), usage (beans available for business logic), and destruction (beans released for garbage collection).
- Initialization itself splits into step A (load and process bean definitions) and step B (actually create and initialize beans, covered in the next lesson).
- Step A only produces *definitions* — a `BeanFactory` mapping bean IDs to bean definitions — with no instances created yet.
- `BeanFactoryPostProcessor` is an extension point that runs after definitions are loaded but before any bean is instantiated, letting you modify any bean's definition.
- `PropertySourcesPlaceholderConfigurer` — the mechanism that resolves `@Value("${...}")` placeholders — is a concrete, built-in example of a `BeanFactoryPostProcessor`, and Spring Boot (or Spring 4.3+) typically registers it for you automatically.
- A custom `BeanFactoryPostProcessor` must be defined via a `static` `@Bean` method, since it needs to run before every other bean in the context.

## Check your understanding

1. What exactly does a `BeanFactoryPostProcessor` operate on, and why is it safe for it to modify anything it wants at that point in the lifecycle?
2. Why must a `@Bean` method that returns a `BeanFactoryPostProcessor` be declared `static`?
3. If you're on a recent version of Spring Boot, do you need to manually register a `PropertySourcesPlaceholderConfigurer` to use `@Value("${...}")`? Why or why not?

The next lesson continues the initialization phase with step B — what actually happens when Spring creates and wires up each bean instance.
