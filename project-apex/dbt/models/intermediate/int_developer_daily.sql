-- int_developer_daily: PR and review metrics aggregated per developer per day.
--
-- Source: stg_github_events + stg_review_records
-- Grain: one row per (developer_login, created_date)
-- Owner: Data Engineering

with prs as (

    select
        developer_login,
        created_date,
        count(*)                                                        as prs_opened,
        countif(is_merged)                                              as prs_merged,
        countif(is_abandoned)                                           as prs_abandoned,

        -- cycle time in hours: only for merged PRs
        avg(
            case when is_merged
                then timestamp_diff(merged_at_utc, created_at_utc, minute) / 60.0
            end
        )                                                               as avg_cycle_time_hours,

        sum(total_churn)                                                as daily_churn,
        avg(additions)                                                  as avg_additions,
        avg(deletions)                                                  as avg_deletions

    from {{ ref('stg_github_events') }}
    where event_type = 'pull_request'
    group by 1, 2

),

reviews as (

    select
        reviewer                                                        as developer_login,
        cast(submitted_at at time zone 'UTC' as date)                   as created_date,
        count(*)                                                        as reviews_submitted,
        avg(review_latency_hours)                                       as avg_review_latency_given_hours

    from {{ source('apex_raw', 'review_records') }}
    group by 1, 2

),

joined as (

    select
        coalesce(p.developer_login, r.developer_login)                  as developer_login,
        coalesce(p.created_date,    r.created_date)                     as activity_date,

        coalesce(p.prs_opened,      0)                                  as prs_opened,
        coalesce(p.prs_merged,      0)                                  as prs_merged,
        coalesce(p.prs_abandoned,   0)                                  as prs_abandoned,
        p.avg_cycle_time_hours,
        coalesce(p.daily_churn,     0)                                  as daily_churn,

        coalesce(r.reviews_submitted, 0)                                as reviews_submitted,
        r.avg_review_latency_given_hours

    from prs p
    full outer join reviews r
        on  p.developer_login = r.developer_login
        and p.created_date    = r.created_date

)

select * from joined
