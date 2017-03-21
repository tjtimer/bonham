import riot from 'riot'
export default riot.tag(
    "loading-indicator",
    `
        <div class="loader-bar">
            <div class="point">o</div>
            <div class="point">o</div>
            <div class="point">o</div>
            <div class="point">o</div>
        </div>
    `
)
