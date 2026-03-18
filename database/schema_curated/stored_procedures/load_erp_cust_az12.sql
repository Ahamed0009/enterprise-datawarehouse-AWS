/*
===============================================================================
Stored Procedure: Load Curated Layer - erp_cust_az12 (Stage -> Curated)
===============================================================================
Script Purpose:
    This stored procedure performs the ETL (Extract, Transform, Load) process to
    populate the 'curated.erp_cust_az12' table from the 'stage.erp_cust_az12' table.

    Actions Performed:
        - Validates the number of records to be loaded using COUNT.
        - Inserts transformed and cleansed data from Stage into Curated table.

Parameters:
    None.
    This stored procedure does not accept any parameters or return any values.

Usage Example:
    CALL curated.load_erp_cust_az12();
===============================================================================
*/

-- DROP PROCEDURE curated.load_erp_cust_az12();

CREATE OR REPLACE PROCEDURE curated.load_erp_cust_az12()
LANGUAGE plpgsql
AS $procedure$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    batch_start_time TIMESTAMP;
    batch_end_time TIMESTAMP;
    record_count BIGINT;
    error_region TEXT;
BEGIN

    batch_start_time := clock_timestamp();

    RAISE NOTICE '================================================';
    RAISE NOTICE 'Loading Table: curated.erp_cust_az12';
    RAISE NOTICE '================================================';

    ------------------------------------------------
    -- COUNT VALIDATION REGION
    ------------------------------------------------
    error_region := 'COUNT VALIDATION REGION';
    start_time := clock_timestamp();
    RAISE NOTICE '>> [START] COUNT VALIDATION REGION';

    SELECT COUNT(*)
    INTO record_count
    FROM (
        SELECT
            -- Old version (commented out for history)
            /*
            CASE
                WHEN "CID" LIKE 'NAS%' THEN SUBSTRING("CID",4)
                ELSE "CID"
            END AS cid,
            CASE
                WHEN TO_DATE("BDATE",'YYYYMMDD') > CURRENT_DATE THEN NULL
                ELSE TO_DATE("BDATE",'YYYYMMDD')
            END AS bdate,
            CASE
                WHEN UPPER(TRIM("GEN")) IN ('F','FEMALE') THEN 'Female'
                WHEN UPPER(TRIM("GEN")) IN ('M','MALE') THEN 'Male'
                ELSE 'n/a'
            END AS gen
            FROM stage.erp_cust_az12
            */
            CASE
                WHEN "CID" LIKE 'NAS%' THEN SUBSTRING(TRIM("CID"),4)
                ELSE TRIM("CID")
            END AS cid,
            CASE
                WHEN TRIM("BDATE") ~ '^\d{4}-\d{2}-\d{2}$' THEN TRIM("BDATE")::DATE
                WHEN TRIM("BDATE") ~ '^\d{8}$' THEN TO_DATE(TRIM("BDATE"),'YYYYMMDD')
                ELSE NULL
            END AS bdate,
            CASE
                WHEN UPPER(TRIM("GEN")) IN ('F','FEMALE') THEN 'Female'
                WHEN UPPER(TRIM("GEN")) IN ('M','MALE') THEN 'Male'
                ELSE 'n/a'
            END AS gen
        FROM stage.erp_cust_az12
    ) src;

    RAISE NOTICE '>> Records to be inserted: %', record_count;
    end_time := clock_timestamp();
    RAISE NOTICE '>> [END] COUNT VALIDATION REGION';
    RAISE NOTICE '>> Duration: % seconds', EXTRACT(EPOCH FROM (end_time - start_time));
    RAISE NOTICE '>> -------------------------------------';

    ------------------------------------------------
    -- INSERT REGION
    ------------------------------------------------
    error_region := 'INSERT REGION';
    start_time := clock_timestamp();
    RAISE NOTICE '>> [START] INSERT REGION';

    TRUNCATE TABLE curated.erp_cust_az12;

    INSERT INTO curated.erp_cust_az12 (cid, bdate, gen)
    SELECT
        -- Old code commented out for history
        /*
        CASE
            WHEN "CID" LIKE 'NAS%' THEN SUBSTRING("CID",4)
            ELSE "CID"
        END,
        CASE
            WHEN TO_DATE("BDATE",'YYYYMMDD') > CURRENT_DATE THEN NULL
            ELSE TO_DATE("BDATE",'YYYYMMDD')
        END,
        CASE
            WHEN UPPER(TRIM("GEN")) IN ('F','FEMALE') THEN 'Female'
            WHEN UPPER(TRIM("GEN")) IN ('M','MALE') THEN 'Male'
            ELSE 'n/a'
        END
        FROM stage.erp_cust_az12
        */
        CASE
            WHEN "CID" LIKE 'NAS%' THEN SUBSTRING(TRIM("CID"),4)
            ELSE TRIM("CID")
        END AS cid,
        CASE
            WHEN TRIM("BDATE") ~ '^\d{4}-\d{2}-\d{2}$' THEN TRIM("BDATE")::DATE
            WHEN TRIM("BDATE") ~ '^\d{8}$' THEN TO_DATE(TRIM("BDATE"),'YYYYMMDD')
            ELSE NULL
        END AS bdate,
        CASE
            WHEN UPPER(TRIM("GEN")) IN ('F','FEMALE') THEN 'Female'
            WHEN UPPER(TRIM("GEN")) IN ('M','MALE') THEN 'Male'
            ELSE 'n/a'
        END AS gen
    FROM stage.erp_cust_az12;

    end_time := clock_timestamp();
    RAISE NOTICE '>> [END] INSERT REGION';
    RAISE NOTICE '>> Load Duration: % seconds', EXTRACT(EPOCH FROM (end_time - start_time));
    RAISE NOTICE '>> -------------------------------------';

    ------------------------------------------------
    -- BATCH COMPLETE
    ------------------------------------------------
    batch_end_time := clock_timestamp();
    RAISE NOTICE '================================================';
    RAISE NOTICE 'Load Completed: curated.erp_cust_az12';
    RAISE NOTICE 'Total Duration: % seconds', EXTRACT(EPOCH FROM (batch_end_time - batch_start_time));
    RAISE NOTICE '================================================';

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '================================================';
        RAISE NOTICE 'ERROR OCCURRED';
        RAISE NOTICE 'Error Region: %', error_region;
        RAISE NOTICE 'Error Message: %', SQLERRM;
        RAISE NOTICE '================================================';
END;
$procedure$;
