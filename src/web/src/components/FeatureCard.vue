<template>
  <div
    class="group relative flex h-full flex-col gap-3 overflow-hidden rounded-2xl border border-white/10 bg-[linear-gradient(180deg,rgba(214,160,96,0.08),rgba(15,15,18,0.30))] p-5 shadow-[0_14px_44px_rgba(0,0,0,0.45)] backdrop-blur-[22px] transition-all duration-200 hover:-translate-y-0.5 hover:border-[rgba(214,160,96,0.35)] hover:shadow-[0_18px_52px_rgba(0,0,0,0.52)]"
  >
    <div
      class="pointer-events-none absolute -right-16 -top-16 h-40 w-40 rounded-full bg-[radial-gradient(circle,rgba(214,160,96,0.22),transparent_70%)] opacity-0 transition-opacity duration-300 group-hover:opacity-100"
      aria-hidden="true"
    ></div>
    <div class="relative flex items-start gap-3">
      <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-[rgba(214,160,96,0.28)] to-[rgba(240,192,122,0.18)] text-[var(--accent-2)]">
        <slot name="icon" />
      </div>
      <div class="min-w-0">
        <div class="text-base font-semibold text-white">
          <slot name="title" />
        </div>
        <div class="mt-1 text-sm leading-relaxed text-white/60">
          <slot name="description" />
        </div>
      </div>
    </div>
    <div v-if="$slots.footer" class="relative mt-auto pt-2">
      <slot name="footer" />
    </div>
  </div>
</template>
