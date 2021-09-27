# Finance Tracker

> Created by TheCrabilia, 26th of September 2021

## Commands

Adds the new expense record to the database.

Amount is **requered**, but category and description are **optional**.

If category is not specified, record will be added to the database with `Unknown` category.

Command syntax:

```
/add <amount> <category> <description>
```

---

This command shows the latest 5 expenses by default. You can specify a nubmer to show more records.

Records are outputed in sorted way, from newest (at the top) to oldest (at the bottom).

Command syntax:

```
/latest <number>
```

---

Top command shows the top 10 biggest spendings.

You can specify any of theese options:

- `day` - shows the top 10 spendings for today.
- `month` - shows the top 10 spendings for current month.
- `year` - shows the top 10 spendings for current year.

Command syntax:

```
/top <day|month|year>
```
