export function color_source_code(code_block) {
    code_block.each(function (i, block) {
        hljs.highlightBlock(block);
    });
}
