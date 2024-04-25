<template>
    <div class="query-error"> {{ error }} </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";

@Component
class QueryError extends Vue {
    @Prop error: string
}

export default toNative(QueryError);

</script>

<style lang="scss" scoped>
.query-error {
    color: red;
}
</style>