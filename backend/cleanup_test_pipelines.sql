-- =====================================================
-- CLEANUP SCRIPT: Delete All Test Transformation Pipelines
-- =====================================================
-- WARNING: This will delete ALL transformation pipelines
-- and their associated steps and runs for your user
-- =====================================================

-- Step 1: Delete all pipeline runs (execution history)
DELETE FROM pipeline_runs
WHERE pipeline_id IN (
    SELECT id FROM transformation_pipelines
    WHERE owner_id = (SELECT id FROM users WHERE email = 'YOUR_EMAIL_HERE')
);

-- Step 2: Delete all transformation steps
DELETE FROM transformation_steps
WHERE pipeline_id IN (
    SELECT id FROM transformation_pipelines
    WHERE owner_id = (SELECT id FROM users WHERE email = 'YOUR_EMAIL_HERE')
);

-- Step 3: Delete all transformation pipelines
DELETE FROM transformation_pipelines
WHERE owner_id = (SELECT id FROM users WHERE email = 'YOUR_EMAIL_HERE');

-- Verify deletion
SELECT
    'Pipelines' as table_name,
    COUNT(*) as remaining_rows
FROM transformation_pipelines
WHERE owner_id = (SELECT id FROM users WHERE email = 'YOUR_EMAIL_HERE')
UNION ALL
SELECT
    'Steps' as table_name,
    COUNT(*) as remaining_rows
FROM transformation_steps
WHERE pipeline_id IN (
    SELECT id FROM transformation_pipelines
    WHERE owner_id = (SELECT id FROM users WHERE email = 'YOUR_EMAIL_HERE')
)
UNION ALL
SELECT
    'Runs' as table_name,
    COUNT(*) as remaining_rows
FROM pipeline_runs
WHERE pipeline_id IN (
    SELECT id FROM transformation_pipelines
    WHERE owner_id = (SELECT id FROM users WHERE email = 'YOUR_EMAIL_HERE')
);
