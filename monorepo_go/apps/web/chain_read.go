package main

import deep "mono/chain_deep"

// chainDeepValue resolves the transitive alias: the LSP must follow
// deep.VALUE_ALIAS → chain_middle.MIDDLE_VALUE → chain_origin.ORIGIN_VALUE.
func chainDeepValue() string {
	return deep.VALUE_ALIAS
}
