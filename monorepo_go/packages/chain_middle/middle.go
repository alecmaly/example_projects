package chain_middle

import origin "mono/chain_origin"

// Go has no true re-export, but a package-level var/const that aliases
// the imported value is the equivalent shape consumers follow.
const MIDDLE_VALUE = origin.ORIGIN_VALUE   // T1.middle.reexport (aliased by assignment)
