# Deployment

For postgres, create the scores table like this:
```
CREATE TABLE scores (
    username    varchar(50),
    easy        integer,
    medium      integer,
    hard        integer,
    date_made   date
);
```

```
vercel --prod .
```

# Todo
- Convert all database usage to Vercel Postgres
- Make frontend and badges look better