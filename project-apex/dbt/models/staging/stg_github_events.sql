-- stg_github_events: clean and type-cast raw GitHub webhook events.
--
-- Source: developer_events table (written by the FastAPI ingestion service)
-- Grain: one row per GitHub event (PR open, PR close, push)
-- Owner: Data Engineering

with source as (

    select * from {{ source('apex_raw', 'developer_events') }}

),

renamed as (

    select
        event_id,
        event_type,
        repo,
        author                                              as developer_login,
        pr_number,

        -- timestamps: cast to UTC and surface as date for easy joining
        created_at at time zone 'UTC'                       as created_at_utc,
        merged_at  at time zone 'UTC'                       as merged_at_utc,
        closed_at  at time zone 'UTC'                       as closed_at_utc,
        cast(created_at as date)                            as created_date,

        -- churn metrics
        additions,
        deletions,
        additions + deletions                               as total_churn,

        -- computed flags
        merged_at is not null                               as is_merged,
        closed_at is not null and merged_at is null         as is_abandoned,

        recorded_at

    from source

    -- exclude test/bot accounts
    where author not like '%[bot]%'
      and author not in ('dependabot', 'renovate')

)

select * from renamed
