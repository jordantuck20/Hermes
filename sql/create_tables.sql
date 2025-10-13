USE hermes_db;

CREATE TABLE guilds (
	guild_id BIGINT UNSIGNED PRIMARY KEY,
    guild_name VARCHAR(255),
    channel_id BIGINT UNSIGNED NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE games (
	app_id INT UNSIGNED PRIMARY KEY,
    game_name VARCHAR(255),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE subscriptions (
	guild_id BIGINT UNSIGNED,
    app_id INT UNSIGNED,
    is_subscribed BOOLEAN DEFAULT TRUE,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (guild_id, app_id),
    FOREIGN KEY (guild_id) REFERENCES guilds(guild_id),
    FOREIGN KEY (app_id) REFERENCES games(app_id)
);

CREATE TABLE news_items (
	news_gid BIGINT UNSIGNED PRIMARY KEY,
    app_id INT UNSIGNED,
    title VARCHAR(255),
    date_fetched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_id) REFERENCES games(app_id)
);

CREATE TABLE delivery_log (
	news_gid BIGINT UNSIGNED,
	guild_id BIGINT UNSIGNED,
    delivery_status VARCHAR(50),
    delivered_at TIMESTAMP NOT NULL,
    attempt_count TINYINT UNSIGNED DEFAULT 1,
    error_details TEXT,
    PRIMARY KEY (news_gid, guild_id),
    FOREIGN KEY (news_gid) REFERENCES news_items(news_gid),
    FOREIGN KEY (guild_id) REFERENCES guilds(guild_id)
);