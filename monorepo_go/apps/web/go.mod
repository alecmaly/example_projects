module mono/apps/web

go 1.22

require (
	mono/shared       v0.0.0
	mono/utils        v0.0.0
	mono/scopes_ns    v0.0.0
	mono/chain_deep   v0.0.0
	mono/chain_middle v0.0.0
	mono/chain_origin v0.0.0
)

// Replace directives are how Go expresses path-dep-to-sibling in a
// multi-module workspace when not using go.work.
replace (
	mono/shared       => ../../packages/shared
	mono/utils        => ../../packages/utils
	mono/scopes_ns    => ../../packages/scopes_ns
	mono/chain_deep   => ../../packages/chain_deep
	mono/chain_middle => ../../packages/chain_middle
	mono/chain_origin => ../../packages/chain_origin
)
