//! Terencher core: domain models and SQLite persistence.
//!
//! This crate is intentionally free of any UI / framework dependency so it can be
//! unit-tested on the host and reused by the Tauri Android shell.

pub mod db;
pub mod models;

pub use models::*;
