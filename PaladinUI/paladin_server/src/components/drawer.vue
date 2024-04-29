<template>
    <div>
        <div class="drawer" :class="{ 'is-open': isOpen, 'is-visible': isVisible }">
            <div
                class="drawer__overlay"
                :style="{ transitionDuration: `${speed}ms` }"
            ></div>
            <div
                class="drawer__content"
                v-click-away="closeDrawer"
                :style="{maxWidth: maxWidth, transitionDuration: `${speed}ms`, backgroundColor: backgroundColor}">
                <slot>
                    <component :is="content" v-bind="contentProps"></component>
                </slot>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue, Watch} from "vue-facing-decorator";
import VueClickAway, {directive} from "vue3-click-away"

@Component({
    components: {VueClickAway},
    directives: {ClickAway: directive},
    emits: ["close"]
})
class Drawer extends Vue {

    @Prop content: any
    @Prop contentProps: any
    @Prop({default: false}) isOpen!: boolean
    @Prop({default: '400px'}) maxWidth!: string
    @Prop({default: '#2b2b2b'}) backgroundColor!: string
    @Prop({default: 250}) speed!: number

    isVisible: boolean = false;
    isTransitioning: boolean = false;

    mounted() {
        this.isVisible = this.isOpen;
    }

    @Watch("isOpen")
    onIsOpenChange(val) {
        this.isTransitioning = true;

        if (val) {
            this.toggleBackgroundScrolling(true);
            this.isVisible = true;
        } else {
            this.toggleBackgroundScrolling(false);
            setTimeout(() => (this.isVisible = false), this.speed);
        }

        setTimeout(() => (this.isTransitioning = false), this.speed);
    }

    toggleBackgroundScrolling(enable) {
        const body = document.querySelector("body");

        body.style.overflow = enable ? "hidden" : null;
    }

    closeDrawer() {
        if (!this.isTransitioning) {
            this.$emit("close");
        }
    }

}

export default toNative(Drawer);

</script>


<style lang="scss" scoped>
.drawer {
    visibility: hidden;

    &.is-visible {
        visibility: visible;
    }

    &.is-open {
        .drawer__overlay {
            opacity: 0.5;
        }

        .drawer__content {
            transform: translateX(0);
        }
    }

    &__overlay {
        position: fixed;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        width: 100%;
        z-index: 200;
        opacity: 0;
        transition-property: opacity;
        background-color: #000000;
        user-select: none;
    }

    &__content {
        position: fixed;
        top: 0;
        right: 0;
        bottom: 0;
        height: 100%;
        width: 100%;
        z-index: 9999;
        overflow: auto;
        transition-property: transform;
        display: flex;
        flex-direction: column;
        transform: translateX(100%);
        box-shadow: 0 2px 6px #777;
    }
}
</style>
