use std::borrow::Borrow;
use std::ops::Deref;

use schemars::{
    JsonSchema,
    Schema,
    SchemaGenerator,
    json_schema,
};
use serde::{
    Deserialize,
    Serialize,
};

/// Subject of the tool name change. For tools in mcp servers, you would need to prefix them with
/// their server names
#[derive(Debug, Clone, Serialize, Deserialize, Eq, Hash, PartialEq, JsonSchema)]
pub struct OriginalToolName(String);

impl Deref for OriginalToolName {
    type Target = String;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl Borrow<str> for OriginalToolName {
    fn borrow(&self) -> &str {
        self.0.as_str()
    }
}

pub fn alias_schema(generator: &mut SchemaGenerator) -> Schema {
    let key_schema = generator.subschema_for::<OriginalToolName>();
    let key_description = key_schema
        .get("description")
        .and_then(|v| v.as_str())
        .unwrap_or("Subject of the tool name change. For tools in mcp servers, you would need to prefix them with their server names");

    json_schema!({
        "type": "object",
        "additionalProperties": {
            "type": "string",
            "description": "The name to change to. For tools in mcp servers, you would need to exclude their server prefix"
        },
        "propertyNames": {
            "type": "string",
            "description": key_description
        }
    })
}

/// The name of the tool to be configured
#[derive(Debug, Clone, Serialize, Deserialize, Eq, Hash, PartialEq, JsonSchema)]
pub struct ToolSettingTarget(String);

impl Deref for ToolSettingTarget {
    type Target = String;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl Borrow<str> for ToolSettingTarget {
    fn borrow(&self) -> &str {
        self.0.as_str()
    }
}

pub fn tool_settings_schema(generator: &mut SchemaGenerator) -> Schema {
    let key_schema = generator.subschema_for::<ToolSettingTarget>();
    let key_description = key_schema
        .get("description")
        .and_then(|v| v.as_str())
        .unwrap_or("The name of the tool to be configured");

    json_schema!({
        "type": "object",
        "additionalProperties": {
            "type": "string",
            "description": "Settings for tools. Refer to our documentations to see how to configure them"
        },
        "propertyNames": {
            "type": "string",
            "description": key_description
        }
    })
}
