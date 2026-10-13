## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain the problems with writing plain, traditional JDBC code
- Recognize the Template design pattern and name a few of Spring's other template classes
- Explain what `JdbcTemplate` takes care of on your behalf when you call a method like `queryForObject`
- Create a `JdbcTemplate` from a `DataSource` and explain why it's safe to reuse a single instance everywhere

## Moving into the data access layer

Interacting with a database is one of the most common tasks in application development, and Java offers multiple APIs for doing it — JDBC being one of them. This module focuses on how Spring simplifies working with JDBC specifically. The plan across this and the next two lessons: first look at the problems with traditional JDBC, then introduce `JdbcTemplate` to fix them, see its basic usage and a more advanced callback-based usage, and finish by looking at how it handles exceptions.

## The problem with plain JDBC

If you've written plain JDBC before, the problems are probably already familiar.

```java
public List<Person> findByLastName(String lastName) {
    List<Person> personList = new ArrayList<>();
    String sql = "select first_name, age from PERSON where last_name=?";

    try (Connection conn = dataSource.getConnection();
         PreparedStatement ps = conn.prepareStatement(sql)) {
        ps.setString(1, lastName);

        try (ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                personList.add(new Person(rs.getString("first_name"), ...));
            }
        }
    } catch (SQLException e) {
        /* ??? */
    }

    return personList;
}
```

A lot of code is needed just to fetch a few people from a database. You define the SQL statement, get a `Connection` from the `DataSource`, prepare the statement — a `PreparedStatement` is required here rather than string concatenation, since you don't want to open the door to SQL injection — execute the query, and iterate over the `ResultSet`, mapping each row into a domain object.

Out of all of that, only two things actually matter: the SQL statement itself, and how a row gets mapped into a domain object. Everything else is boilerplate that provides no value on its own — it's just plumbing you're forced to write every time.

On top of that, JDBC's `SQLException` is a checked exception, so you're forced to catch it somewhere. But is this method the right place to actually *handle* that exception? Usually not — SQL exceptions tend to be fatal, and they're a fairly generic, leaky abstraction that doesn't tell you much you can act on at this call site. Do you log it? Rethrow it? At this point in the code, there often isn't a good answer.

## Introducing `JdbcTemplate`

`JdbcTemplate` exists to strip away that boilerplate while keeping all of the JDBC API's power available to you.

The name is a hint: it ends in "Template" because it implements the **Template design pattern** — a widely used pattern where you define the outline, or skeleton, of an algorithm and leave the details of specific steps to be filled in later, typically by passing in a callback. This is what lets `JdbcTemplate` hide away large amounts of boilerplate code while still letting you plug in exactly the parts that are specific to your query.

Spring provides many template classes built on this same pattern: `JdbcTemplate` and `JmsTemplate`, `RestTemplate` and `WebServiceTemplate`, and others you'll encounter elsewhere in the framework (including `RabbitTemplate` and `KafkaTemplate`). All of them share the same idea — hide low-level resource management, expose just the parts you actually care about.

`JdbcTemplate` itself is one of the oldest classes in the framework, originally written by Rod Johnson, the founder of Spring.

> "Life is too short to write JDBC!" — Rod Johnson, co-founder of Spring

`JdbcTemplate` greatly simplifies use of the JDBC API — eliminating repetitive boilerplate code, alleviating common causes of bugs, and handling `SQLException`s properly — without sacrificing power: it still provides full access to the standard JDBC constructs whenever you need them. There's essentially no downside to reaching for `JdbcTemplate` any time you're using the JDBC API.

## What one line of `JdbcTemplate` actually does

```java
int count = jdbcTemplate.queryForObject(
    "SELECT COUNT(*) FROM CUSTOMER", Integer.class);
```

This single line quietly handles a whole sequence of steps on your behalf, all inside the template: acquisition of the connection, participation in the transaction, execution of the statement, processing of the result set, handling exceptions, and release of the connection (potentially back into a connection pool). Compare that to the hand-written `try`/`catch`/`finally` block from the plain-JDBC example — it's the exact same responsibilities, just handled for you.

## Using callbacks

Because `JdbcTemplate` implements the Template pattern, you can pass it callbacks to plug in your own logic at exactly the point where it's needed.

```java
List<Customer> results = jdbcTemplate.query(someSql,
    new RowMapper<Customer>() {
        public Customer mapRow(ResultSet rs, int row) throws SQLException {
            // map the current row to a Customer object
        }
    });
```

The callback shown here is called a **`RowMapper`** — one of several callback types `JdbcTemplate` supports (more are covered in the next lesson). A `RowMapper` is parameterized by the type you want back; you implement only the mapping logic — given a `ResultSet` and the current row, produce a `Customer` — and the template handles everything else.

Looking at what `query()` does conceptually: it acquires the connection, prepares the statement, executes it, and then for every row in the result set, it invokes your `RowMapper` callback and adds the result to a list, which is what ultimately gets returned. `JdbcTemplate` also catches the `SQLException` and releases the connection along the way. You only ever write the SQL statement and the row-mapping logic — the boilerplate stays inside the template.

## Creating a `JdbcTemplate`

`JdbcTemplate` requires only a `DataSource`, since that's what it needs in order to obtain a connection:

```java
JdbcTemplate template = new JdbcTemplate(dataSource);
```

You should create a template once and reuse it everywhere — there's no need for a new instance per thread, since `JdbcTemplate` is thread-safe once constructed. In practice this is usually a Spring-managed bean, injected wherever it's needed, rather than something you construct by hand in application code.

Beyond everyday application repositories, `JdbcTemplate` is also useful any time JDBC is needed in utility or test code, or to clean up messy legacy code — for example, using it inside a test to directly verify something landed in the database, even if your application otherwise uses a higher-level persistence API.

## Recap

- Plain JDBC forces you to write a large amount of boilerplate (connections, prepared statements, result set iteration, exception handling) around the only two things that actually matter: the SQL statement and the row-mapping logic.
- `SQLException` is checked and generic, which usually means there's no meaningful way to handle it at the point it's thrown.
- `JdbcTemplate` implements the Template design pattern, the same pattern behind other Spring templates like `RestTemplate` and `JmsTemplate`.
- A single `JdbcTemplate` call (e.g., `queryForObject`) handles connection acquisition, transaction participation, statement execution, result processing, exception handling, and connection release.
- Callbacks like `RowMapper` let you plug in just the row-mapping logic while `JdbcTemplate` handles the rest.
- `JdbcTemplate` needs only a `DataSource`, is thread-safe, and should be created once and reused everywhere.

## Check your understanding

1. In the plain JDBC example, which two pieces of the method actually matter, and which parts are boilerplate that `JdbcTemplate` eliminates?
2. What design pattern does `JdbcTemplate` implement, and name two other Spring classes that implement the same pattern.
3. What does a `RowMapper` callback let you avoid writing, and what does it still leave you responsible for?

The next lesson digs deeper into `JdbcTemplate`'s basic usage — the query and update methods you'll reach for most often.
