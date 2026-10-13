## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Define what the Spring Framework actually is
- Explain why Spring is open source, lightweight, and non-invasive, and why each of those matters
- Describe what the DI container does, at a high level
- Recognize that Spring is much more than just its container — it's an integration layer for the rest of your application's needs

## What is the Spring Framework?

The Spring Framework simplifies the development of enterprise applications. It's important that it's a **framework** and not just a library: a library is something you call from your code, but a framework helps you in every part of your application — the web layer, the data access layer, security, and more.

This lesson stays at the conceptual level — no implementation details yet. Those come in later lessons. For now, the goal is simply to understand what Spring is, when you'd reach for it, why it's so popular, and the range of applications you can build with it.

## Spring is open source

All of Spring's source and binary code is freely available, under an Apache 2 license:

- Source code: <a href="https://github.com/spring-projects/spring-framework" target="_blank" rel="noopener noreferrer">https://github.com/spring-projects/spring-framework</a>
- Binaries: available at <a href="https://central.sonatype.com/namespace/org.springframework" target="_blank" rel="noopener noreferrer">Maven Central</a>
- Documentation: <a href="https://docs.spring.io/spring/docs/current/spring-framework-reference/htmlsingle" target="_blank" rel="noopener noreferrer">https://docs.spring.io/spring/docs/current/spring-framework-reference/htmlsingle</a>

Being open source also means there's a large community constantly contributing to the framework. A quick practical note: the use of a transitive dependency management system (Maven, Gradle, or Ant/Ivy) is recommended for any Java application that pulls in Spring — you'll rely on this throughout the course to manage the framework's own dependencies for you.

## Spring is lightweight

Unlike the old J2EE model, Spring applications don't require a Java EE application server to run — though they certainly *can* be deployed on one if you want. Spring is also **not invasive**: it doesn't require you to extend framework classes or implement framework interfaces for most usage. You write your own code as POJOs (Plain Old Java Objects), and Spring adds behavior on top of that business logic rather than forcing your business logic to live inside its own class hierarchy.

On top of that, Spring has low overhead — the JARs used in this course are all under 8MB.

## Spring provides a DI container

At Spring's core is the **Dependency Injection (DI) container** — sometimes also called an **Inversion of Control (IoC) container**. This is where you'll spend the first several modules of this course: configuring the container, also known as the application context.

The container does three things for your application objects:

- Your objects don't have to worry about finding or connecting to each other — the container wires that up for you
- Spring instantiates and injects dependencies into your objects
- Spring also serves as a **lifecycle manager** — taking your components through initialization, use, and destruction

## Spring is more than just a DI container

The container is the foundation, but enterprise applications need to deal with a much wider variety of technologies, architectures, and deployment platforms than just object wiring:

- Containerization, cloud, micro-services
- JDBC, transactions, ORM/JPA, NoSQL
- Events, streaming, reactive programming, messaging (JMS, AMQP), tasks, scheduling
- Security, OAuth2, OpenID Connect
- Monitoring, observability

Spring provides framework classes, interfaces, and annotations to simplify working with all of these lower-level technologies, and it's highly extensible and customizable — you can swap in your own behavior anywhere you need to.

## Where to find the rest of the portfolio

As an open source project, the whole Spring portfolio lives at <a href="https://github.com/spring-projects" target="_blank" rel="noopener noreferrer">github.com/spring-projects</a>. The Spring Framework you're learning here is just the core — beyond it you'll find sibling projects like Spring Data and Spring Security, all under an Apache 2 license and published to Maven Central. Each project in the portfolio has its own dedicated documentation.

Next up is **The Dependency Injection (DI) Container**, where you'll dig into how that container actually manages your components' dependencies.
