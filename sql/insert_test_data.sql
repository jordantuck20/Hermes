USE hermes_db;

INSERT INTO guilds (guild_id, guild_name, channel_id) VALUES
(123456789012345678, 'Test Guild 1', 987654321098765432),
(234567890123456789, 'Test Guild 2', 876543210987654321),
(345678901234567890, 'Test Guild 3', 765432109876543210);

INSERT INTO games (app_id, game_name, is_active) VALUES
(2807960, 'Battlefield 6', TRUE),
(553850, 'Helldivers 2', TRUE),
(3527290, 'Peak', FALSE); -- Set to inactive to test subscription filtering

INSERT INTO subscriptions (guild_id, app_id, is_subscribed) VALUES
-- Test Guild 1 is subscribed to Battlefield 6 and Helldivers 2
(123456789012345678, 2807960, TRUE),
(123456789012345678, 553850, TRUE),

-- Test Guild 2 is subscribed to Battlefield 6 and Helldivers 2, with Helldivers 2 subscription paused
(234567890123456789, 2807960, TRUE),
(234567890123456789, 553850, FALSE),

-- Test Guild 3 is subscribed to all 3
(345678901234567890, 2807960, TRUE),
(345678901234567890, 553850, TRUE),
(345678901234567890, 3527290, TRUE); -- subscribed to an inactive game

INSERT INTO news_items (news_gid, app_id, title) VALUES
(400000000000000001, 2807960, 'BF6: Post-Release Hotfix'),
(400000000000000002, 553850, 'HELLDIVERS 2: Tech Blog #1'),
(400000000000000003, 553850, 'State of the Game Update #1'),
(400000000000000004, 3527290, 'PEAK: Friday Dev Blog');

INSERT INTO delivery_log (news_gid, guild_id, delivery_status, delivered_at, attempt_count, error_details) VALUES
-- Successful deliveries
(400000000000000001, 123456789012345678, 'SUCCESS', NOW(), 1, NULL),
(400000000000000001, 234567890123456789, 'SUCCESS', NOW(), 1, NULL),
(400000000000000003, 123456789012345678, 'SUCCESS', NOW(), 2, NULL),

-- Attempted and Failed (due to missing permission, maxed our retries)
(400000000000000002, 123456789012345678, 'PERMANENT_FAILURE', NOW(), 3, 'Discord API Error 50001: Missing Access'),

-- Currently pending retry (failed once, waiting for next job)
(400000000000000003, 345678901234567890, 'PENDING_RETRY', NOW(), 2, NULL);