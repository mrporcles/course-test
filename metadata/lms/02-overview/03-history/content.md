## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain the problem Spring was originally created to solve, and who created it
- List a few of the reasons Spring has remained successful for two decades
- Describe how Spring has adapted to new technologies over time
- Recognize the breadth of application types Spring can support today

## Why is Spring successful?

Spring has been around a long time — its first release came out in 2003. So why has it lasted, and why did it take off in the first place?

Back then, the dominant enterprise Java model was J2EE, which typically required implementing a lot of interfaces and extending a lot of classes. That made code difficult to test, and expensive to run, since you generally needed a full application server just to execute it.

A developer named **Rod Johnson** believed there was a better, easier way to build enterprise applications, and wrote the book *J2EE Design and Development*. In it, he introduced principles that would go on to become the foundation of the Spring Framework — things like configuration via dependency injection, and the POJO programming model you saw in the "The Dependency Injection (DI) Container" lesson. Spring quickly became popular as a lighter-weight replacement for J2EE.

A few more reasons for its staying power:

- Spring provides choice at every level, rather than locking you into one way of doing things
- It has embraced change and different perspectives over the years, while working hard to maintain backwards compatibility
- Its source code holds itself to a high standard — the API has been carefully thought through
- It has a huge, welcoming community, visible in the forums, on Stack Overflow, in user groups, and at conferences

## Spring excels at being adaptable to change

Spring has consistently driven innovation and adapted as the ecosystem around it changed:

![Spring excels at being adaptable to change](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/02-overview/03-history/images/lesson4-adaptable-to-change-timeline.png)

- Early on, it integrated with open source projects like Hibernate for persistence, or Quartz for scheduling, and with different templating technologies for server-side rendering
- It created independent projects for entire domains, like Spring Security, Spring Batch, and Spring Integration
- As new domains emerged, it created projects for those too — Spring Data for NoSQL and JPA, Spring Cloud
- It simplified the developer experience directly with **Spring Boot**
- It's adopted new languages, like Kotlin, and newer runtime models like GraalVM native images

## What is Spring used for?

Technically, you can implement almost anything with Spring. One of its central goals is to eliminate boilerplate so you can focus on business logic — if you need to integrate with some framework, Spring aims to provide that integration for you rather than making you build it yourself.

Spring is used to build enterprise applications dealing with:

- **Web apps**
- **Messaging**
- **Persistence** (relational databases or NoSQL data stores)
- **Batch/Tasks**
- **Integration/Streaming**

## The current world

Spring keeps adapting to whatever's current:

- Support for the latest JDK versions
- Native compilation (GraalVM)
- Reactive programming models across the portfolio
- Stream processing
- Kotlin support
- Kubernetes — Spring applications can be packaged as Docker containers, and Spring provides features like health checks that Kubernetes relies on for orchestration

Up next is your first hands-on exercise, **Walkthrough - Spring Overview Lab**, where you'll get familiar with the reward network application you'll be using throughout the rest of the course.
