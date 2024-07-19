<template>
    <div class="empty-results"> Query returned with no results. </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";

@Component
class EmptyResults extends Vue {
}

export default toNative(EmptyResults);

</script>

<style lang="scss" scoped>
.empty-results {
    color: darkorange;
}
</style>