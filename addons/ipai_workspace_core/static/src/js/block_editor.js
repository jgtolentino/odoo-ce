/** @odoo-module **/

/**
 * IPAI Workspace Core - Block Editor Foundation
 *
 * This module provides the foundation for a block-based editor.
 * The full TipTap/ProseMirror integration will be added in Sprint 3.
 *
 * Current features:
 * - Slash command detection
 * - Wiki-link [[Page]] parsing
 * - Todo checkbox toggling
 * - Block type switching
 */

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Block types supported by the editor
 */
export const BLOCK_TYPES = {
    paragraph: { label: "Text", icon: "📝", shortcut: "/text" },
    heading_1: { label: "Heading 1", icon: "H1", shortcut: "/h1" },
    heading_2: { label: "Heading 2", icon: "H2", shortcut: "/h2" },
    heading_3: { label: "Heading 3", icon: "H3", shortcut: "/h3" },
    bulleted_list: { label: "Bulleted List", icon: "•", shortcut: "/bullet" },
    numbered_list: { label: "Numbered List", icon: "1.", shortcut: "/number" },
    todo: { label: "To-do", icon: "☐", shortcut: "/todo" },
    quote: { label: "Quote", icon: "❝", shortcut: "/quote" },
    callout: { label: "Callout", icon: "💡", shortcut: "/callout" },
    divider: { label: "Divider", icon: "—", shortcut: "/divider" },
    code: { label: "Code", icon: "</>", shortcut: "/code" },
};

/**
 * Parse wiki-style links from content
 * @param {string} content - Text content to parse
 * @returns {Array} Array of {text, pageName} objects
 */
export function parseWikiLinks(content) {
    const links = [];
    const regex = /\[\[([^\]]+)\]\]/g;
    let match;

    while ((match = regex.exec(content)) !== null) {
        links.push({
            fullMatch: match[0],
            pageName: match[1],
            index: match.index,
        });
    }

    return links;
}

/**
 * Detect slash commands in text
 * @param {string} text - Text to check
 * @returns {Object|null} Detected command or null
 */
export function detectSlashCommand(text) {
    const match = text.match(/\/(\w+)$/);
    if (!match) return null;

    const command = match[1].toLowerCase();

    for (const [type, config] of Object.entries(BLOCK_TYPES)) {
        if (config.shortcut.toLowerCase() === `/${command}`) {
            return { type, config, match: match[0] };
        }
    }

    // Fuzzy match
    const fuzzyMatches = Object.entries(BLOCK_TYPES).filter(([type, config]) =>
        type.includes(command) || config.label.toLowerCase().includes(command)
    );

    if (fuzzyMatches.length === 1) {
        return { type: fuzzyMatches[0][0], config: fuzzyMatches[0][1], match: match[0] };
    }

    return { type: null, suggestions: fuzzyMatches, match: match[0] };
}

/**
 * Block Editor Service
 * Handles block operations and API calls
 */
export const blockEditorService = {
    dependencies: ["rpc", "notification"],

    start(env, { rpc, notification }) {
        return {
            /**
             * Create a new block
             */
            async createBlock(pageId, blockType, content, sequence) {
                try {
                    const result = await rpc("/workspace/api/block/create", {
                        page_id: pageId,
                        block_type: blockType,
                        content: content,
                        sequence: sequence,
                    });
                    return result;
                } catch (error) {
                    notification.add("Failed to create block", { type: "danger" });
                    throw error;
                }
            },

            /**
             * Update an existing block
             */
            async updateBlock(blockId, data) {
                try {
                    const result = await rpc(`/workspace/api/block/${blockId}`, data);
                    return result;
                } catch (error) {
                    notification.add("Failed to update block", { type: "danger" });
                    throw error;
                }
            },

            /**
             * Delete a block
             */
            async deleteBlock(blockId) {
                try {
                    const result = await rpc(`/workspace/api/block/${blockId}/delete`, {});
                    return result;
                } catch (error) {
                    notification.add("Failed to delete block", { type: "danger" });
                    throw error;
                }
            },

            /**
             * Toggle todo completion
             */
            async toggleTodo(blockId) {
                try {
                    const result = await rpc(`/workspace/api/block/toggle/${blockId}`, {});
                    return result;
                } catch (error) {
                    notification.add("Failed to toggle todo", { type: "danger" });
                    throw error;
                }
            },

            /**
             * Get page data with blocks
             */
            async getPage(pageId) {
                try {
                    const result = await rpc(`/workspace/api/page/${pageId}`);
                    return result;
                } catch (error) {
                    notification.add("Failed to load page", { type: "danger" });
                    throw error;
                }
            },

            /**
             * Save page content
             */
            async savePage(pageId, data) {
                try {
                    const result = await rpc(`/workspace/api/page/${pageId}/save`, data);
                    notification.add("Page saved", { type: "success" });
                    return result;
                } catch (error) {
                    notification.add("Failed to save page", { type: "danger" });
                    throw error;
                }
            },

            /**
             * Search for pages (for [[]] linking)
             */
            async searchPages(query, workspaceId) {
                try {
                    const result = await rpc("/workspace/api/search", {
                        query: query,
                        workspace_id: workspaceId,
                        limit: 10,
                    });
                    return result;
                } catch (error) {
                    console.error("Page search failed:", error);
                    return [];
                }
            },

            /**
             * Get available templates
             */
            async getTemplates(workspaceId, category) {
                try {
                    const result = await rpc("/workspace/api/templates", {
                        workspace_id: workspaceId,
                        category: category,
                    });
                    return result;
                } catch (error) {
                    console.error("Failed to load templates:", error);
                    return [];
                }
            },
        };
    },
};

// Register the service
registry.category("services").add("blockEditor", blockEditorService);

/**
 * Keyboard shortcuts handler for the editor
 */
export function setupKeyboardShortcuts(element, handlers) {
    element.addEventListener("keydown", (event) => {
        // Ctrl/Cmd + S: Save
        if ((event.ctrlKey || event.metaKey) && event.key === "s") {
            event.preventDefault();
            handlers.onSave?.();
        }

        // Ctrl/Cmd + B: Bold
        if ((event.ctrlKey || event.metaKey) && event.key === "b") {
            event.preventDefault();
            handlers.onBold?.();
        }

        // Ctrl/Cmd + I: Italic
        if ((event.ctrlKey || event.metaKey) && event.key === "i") {
            event.preventDefault();
            handlers.onItalic?.();
        }

        // Ctrl/Cmd + K: Insert link
        if ((event.ctrlKey || event.metaKey) && event.key === "k") {
            event.preventDefault();
            handlers.onLink?.();
        }

        // Tab: Indent
        if (event.key === "Tab" && !event.shiftKey) {
            event.preventDefault();
            handlers.onIndent?.();
        }

        // Shift+Tab: Outdent
        if (event.key === "Tab" && event.shiftKey) {
            event.preventDefault();
            handlers.onOutdent?.();
        }

        // Enter: New block
        if (event.key === "Enter" && !event.shiftKey) {
            handlers.onNewBlock?.(event);
        }

        // Backspace at start: Merge with previous
        if (event.key === "Backspace") {
            handlers.onBackspace?.(event);
        }
    });
}

// Export utilities for use in other modules
export default {
    BLOCK_TYPES,
    parseWikiLinks,
    detectSlashCommand,
    setupKeyboardShortcuts,
};
