## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain the difference between checked and unchecked exceptions, and why that distinction matters for API design
- Describe the problem with `SQLException` as the single exception type for every JDBC error
- Explain how Spring translates vendor-specific `SQLException`s into its own `DataAccessException` hierarchy
- Recognize a few key members of that hierarchy, such as `BadSqlGrammarException`
- Explain why the `JdbcTemplate` you've been using never required you to write a single `try`/`catch` block

## Checked vs. unchecked exceptions

Java has two categories of exceptions, and the distinction drives everything in this lesson.

**Checked exceptions** force the caller to handle them: you either wrap the call in a `try`/`catch` block, or your method declares `throws` and passes the problem up. `SQLException` is a classic example. The trouble is that if you want to handle the exception several layers up the call stack, *every intermediate method* in between has to declare that it throws it too, even if it does nothing with it. That's a form of tight coupling between layers that have no real business knowing about each other.

**Unchecked exceptions**, by contrast, can simply be thrown without any of that ceremony. They bubble up the call hierarchy on their own, and you decide, at whatever level makes sense, where to actually catch and handle them. Methods in between don't need to know the exception even exists — which tends to be a better fit for a typical enterprise application, where the code that can meaningfully react to a database error is often far removed from the code that triggered it.

This is the rule to remember: **Spring always throws runtime (unchecked) exceptions.** With the plain JDBC API, you get checked `SQLException`s instead.

## What's wrong with `SQLException`

`SQLException` has a few problems that make it a poor fit for application code:

- It's **too general** — there's exactly one exception type for every possible database error, from a typo in a column name to a broken connection to a constraint violation.
- The calling class "knows" it's talking to JDBC specifically, which is a form of tight coupling to a particular data access technology.
- It often carries **vendor-specific error codes and messages** that aren't meaningful outside the context of that particular database driver.
- It's a **checked** exception, with all the declaration overhead described above.

Spring's answer is the **`DataAccessException`** hierarchy:

- It hides whether you're using JDBC, JPA, Hibernate, or something else entirely — the calling code doesn't need to know or care.
- It's actually a **hierarchy** of sub-exceptions, not one catch-all type — so you get a specific, meaningful exception type for a specific kind of problem, rather than one exception standing in for everything.
- It's **consistent** across every data access technology Spring supports — if you switch from JDBC to JPA, the exceptions your calling code deals with stay the same.
- It's **unchecked**, so it doesn't force try/catch or `throws` declarations onto layers that can't do anything useful with the failure anyway.

## Seeing the translation in action: `BadSqlGrammarException`

The clearest way to see this translation is with a concrete example. Suppose the SQL statement `SELECT iddd FROM T_ACCOUNT` runs against the database — note the typo: `iddd` isn't a real column.

![Plain JDBC surfaces a generic SQLException; Spring maps it into a specific, meaningful exception](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/09-jdbc/04-exception-handling/images/lesson36-badsqlgrammarexception-example.png)

With **plain JDBC**, this fails with a `java.sql.SQLException`, carrying the message `Column not found: IDDD in statement` and an `errorCode` of `-28`. That error code is specific to the database vendor in use here — it's not documented or meaningful to your application code at all.

With **Spring**, that same underlying `SQLException` gets wrapped into a `BadSqlGrammarException` — a much more meaningful, specific exception type that clearly communicates "there was a problem with your SQL grammar," with the original vendor detail preserved inside the message for debugging.

This mapping isn't guesswork — Spring maintains an XML file (`sql-error-codes.xml`, in the `spring-jdbc` source) that maps vendor-specific error codes, for every supported database, onto the correct exception type in the hierarchy. That's how Spring can reliably turn a `-28` from this particular vendor into a `BadSqlGrammarException`, while a different code from the same vendor — or an equivalent code from a completely different vendor — lands on the correct, matching type.

## The `DataAccessException` hierarchy

`DataAccessException` sits at the top of this hierarchy and extends from `RuntimeException`, which is exactly what makes it unchecked. Below it are a range of child exceptions, each representing a specific category of problem in the data access layer:

![DataAccessException hierarchy: BadSqlGrammarException, DataIntegrityViolationException, OptimisticLockingFailureException, and more](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/09-jdbc/04-exception-handling/images/lesson36-data-access-exception-hierarchy.png)

- **`DataAccessResourceFailureException`** — something went wrong acquiring the underlying resource (e.g., the connection itself)
- **`CleanupFailureDataAccessException`** — a failure occurred while cleaning up after an operation
- **`OptimisticLockingFailureException`** — an optimistic locking check failed
- **`BadSqlGrammarException`** — the SQL statement itself was malformed, as in the example above
- **`DataIntegrityViolationException`** — a database integrity constraint (like a unique key or foreign key) was violated

Every one of these is unchecked, so they'll be thrown and bubble up the call hierarchy, but you get to decide where — and whether — to catch them.

Next up is a hands-on lab that puts everything from this JDBC module into practice: refactoring a repository built on plain JDBC over to `JdbcTemplate`, row mappers, and result set extractors.
