-- fct_team_velocity_weekly: weekly velocity and review health per team.
--
-- Source: int_developer_daily
-- Grain: one row per (team, iso_week)
-- Owner: Data Engineering
-- Used by: Apex dashboard — "Team Summary" view (AC-04, AC-05)

with daily as (

    select * from {{ ref('int_developer_daily') }}

),

-- map developers to teams via a seed file (see seeds/team_membership.csv)
team_mapping as (

    select * from {{ ref('team_membership') }}

),

daily_with_team as (

    select
        d.*,
        coalesce(t.team_id, 'unassigned')                       as team_id,
        date_trunc(d.activity_date, week(monday))               as week_start

    from daily d
    left join team_mapping t on d.developer_login = t.developer_login

),

weekly as (

    select
        team_id,
        week_start,
        count(distinct developer_login)                         as active_contributors,
        sum(prs_merged)                                         as prs_merged,
        sum(prs_opened)                                         as prs_opened,
        sum(prs_abandoned)                                      as prs_abandoned,

        -- cycle time stats
        avg(avg_cycle_time_hours)                               as avg_cycle_time_hours,
        approx_quantiles(avg_cycle_time_hours, 100)[offset(50)] as p50_cycle_time_hours,
        approx_quantiles(avg_cycle_time_hours, 100)[offset(90)] as p90_cycle_time_hours,

        -- review health
        sum(reviews_submitted)                                  as reviews_submitted,
        avg(avg_review_latency_given_hours)                     as avg_review_latency_hours,

        -- churn
        sum(daily_churn)                                        as total_churn,
        avg(avg_additions)                                      as avg_pr_additions

    from daily_with_team
    group by 1, 2

)

select * from weekly
