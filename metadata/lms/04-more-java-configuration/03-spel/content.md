## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain where SpEL came from and how it relates to the Unified Expression Language
- Use `@Value` with a `#{...}` expression, rather than the `${...}` property syntax, to evaluate a SpEL expression
- Use SpEL to reach into another Spring-managed bean and read one of its properties
- Explain why properties resolved through SpEL are always strings, and how to work around that
- Provide a fallback value using either the `:` or the Elvis (`?:`) operator

## What SpEL is, and where it came from

**SpEL** — the **Spring Expression Language**, "SpEL" for short — will look familiar if you've used the Unified Expression Language from JSP and JSF, since it was inspired by exactly that. It's more powerful, though, and it has one particularly useful trait for Spring applications: it can interact directly with your Spring-managed beans.

SpEL actually started life inside a project called **Spring WebFlow**, but it was later made available in Spring's core, so every project in the wider Spring portfolio could use it. This lesson focuses specifically on how SpEL is used at the configuration level, but it's worth knowing that other projects — Spring Integration, Spring Security, Spring Batch, among others — also use the expression language and extend it with their own needs, adding their own implicit variables and methods so you can interact with concepts specific to those projects.

*(This lesson is only a brief introduction — for full detail, see the official Spring documentation on expressions.)*

## Writing your first SpEL expression

Recall `@Value` from the "Use External Properties" lesson, where a dollar sign (`${...}`) was used to resolve a value from the `Environment`. SpEL uses a different sign — the hash (`#{...}`) — and expects a full expression rather than a plain property key.

```java
@Configuration
class TaxConfig {

    @Value("#{ systemProperties['user.region'] }") String region;

    @Bean
    public TaxCalculator taxCalculator1() {
        return new TaxCalculator(region);
    }

    @Bean
    public TaxCalculator taxCalculator2(
            @Value("#{ systemProperties['user.region'] }") String region, ...) {
        return new TaxCalculator(region);
    }
}
```

Here, `systemProperties` is an **implicit variable** provided automatically by Spring — you didn't have to define it. The expression asks for `user.region` from `systemProperties`, and the result of evaluating it gets injected into a `String region`.

The example shows two equivalent ways to use this:

- **Option 1** (`taxCalculator1`): set an attribute — here, the `region` field — once, using `@Value`, and then use that field wherever it's needed.
- **Option 2** (`taxCalculator2`): skip the field entirely and annotate the bean method's argument directly with the same `@Value` expression, so it's resolved right where it's used.

## Reaching into another Spring bean

Because SpEL expressions are evaluated against the application context, they can reference other Spring-managed beans directly — not just implicit variables like `systemProperties`.

```java
class StrategyBean {
    private KeyGenerator gen = new KeyGenerator.getInstance("Blowfish");
    public KeyGenerator getKeyGenerator() { return gen; }
}

@Configuration
class StrategyConfig {
    @Bean public StrategyBean strategyBean() {
        return new StrategyBean();
    }
}

@Configuration
@Import(StrategyConfig.class)
class AnotherConfig {
    @Value("#{strategyBean.keyGenerator}") KeyGenerator kgen;
    // ...
}
```

Walking through this: `StrategyBean` is a plain component with a `keyGenerator` field and a `getKeyGenerator()` getter. It's registered as an ordinary bean, named `strategyBean`, inside `StrategyConfig` — nothing new there. `AnotherConfig` then imports `StrategyConfig` and uses a SpEL expression, `#{strategyBean.keyGenerator}`, to reach into that bean.

Two details make this work:

- **`strategyBean` is the bean's name** — and by default, recall from earlier lessons, a bean's name is the name of the `@Bean` method that defines it (here, the method was literally called `strategyBean()`).
- **When SpEL doesn't recognize an implicit variable name, it looks for a matching bean.** Since there's no implicit variable called `strategyBean`, Spring instead looks for a bean with that name in the application context, finds it, and lets the rest of the expression — `.keyGenerator`, calling the `getKeyGenerator()` getter — navigate into its properties.

The evaluated result — the `KeyGenerator` instance — is injected into the `kgen` field. (Worth noting: this is just an illustrative example of SpEL reaching into a bean. In practice, if you just wanted the `KeyGenerator` object itself, injecting `StrategyBean` directly with `@Autowired` and calling its getter in Java would usually be the more natural choice.)

## Properties resolved through SpEL are always strings

Whether you use `${...}` or `#{...}`, a resolved property always comes back as a **string** — Spring performs an implicit conversion afterward, to whatever type your field or argument actually declares:

```java
@Value("${daily.limit}") int maxTransfersPerDay;
@Value("#{environment['daily.limit']}") int maxTransfersPerDay;
```

These two are equivalent, and both work fine, because Spring converts the resolved string into an `int` automatically to match the target type.

That implicit conversion only goes so far, though. If you want to actually *operate* on a property's value from **inside** the expression itself — rather than just letting Spring convert the final result — you have to cast it explicitly:

```java
@Value("#{new Integer(environment['daily.limit']) * 2}")   // OK
@Value("#{new java.net.URL(environment['home.page']).host}")  // OK
@Value("#{daily.limit * 2}")   // NOT OK
```

The first example casts the resolved value to an `Integer` before multiplying it by two — that works. The second casts it to a `URL` in order to call `.host` on it — that also works. The third tries to multiply `daily.limit` by two without ever casting it first, and that fails, because as far as the expression itself is concerned, `daily.limit` is just a string, and you can't multiply a string.

## Providing a fallback value

Sometimes a property might not be defined at all — for that case, both `${...}` and `#{...}` support a fallback value.

With the dollar-sign syntax, use a colon:

```java
@Autowired
public TransferServiceImpl(@Value("${daily.limit : 100000}") int max) {
    this.maxTransfersPerDay = max;
}
```

If `daily.limit` isn't defined (or resolves to null), `100000` is used instead.

With a SpEL expression, the equivalent is the **Elvis operator**, `?:` — named for its sideways-smiley-face resemblance:

```java
@Autowired
public setLimit(@Value("#{environment['daily.limit'] ?: 100000}") int max) {
    this.maxTransfersPerDay = max;
}
```

`x ?: y` is shorthand for "`x` if `x != null`, otherwise `y`" — exactly the same equivalent-operators relationship as the ordinary ternary `x ? y : z`, just specialized for the common "use this, or fall back to a default" case.

## Implicit variables, and how other projects extend them

To summarize what an expression's attributes can actually refer to:

- **Spring beans** — like `strategyBean` in the earlier example.
- **Implicit references** — `environment`, `systemProperties`, and `systemEnvironment` are available by default; others may be available depending on context.
- SpEL allows you to create custom functions and references of your own, too.

And as mentioned at the start of this lesson, SpEL is widely used across the Spring portfolio, with each project adding its own implicit references on top of the core set:

- **Spring Security, Spring WebFlow**
- **Spring Batch, Spring Integration**

Each of these may add their own implicit references — for example, Spring Security lets you access `principal`, representing the current user, inside a SpEL expression. That's a topic for when Spring Security itself is covered later on; for now, the important thing is knowing that the core set of implicit variables (`environment`, `systemProperties`, `systemEnvironment`, and bean names) can be extended by whichever other Spring projects you bring in.

That closes out this module on Java-based configuration — externalized properties, profiles, and now SpEL. Next up is the module quiz, where you can check your understanding of these topics before moving on to annotation-based configuration and component scanning.
