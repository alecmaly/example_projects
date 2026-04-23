-- C1.a — Haskell cycles require a .hs-boot file OR same-module
-- mutual recursion. Cross-module cycles are rare; the idiomatic fix
-- is `.hs-boot`. Here we use mutual rec in a single file to keep
-- the fixture simple (still exercises the LSP's mutual-def tracking).

module CycleA where

data Alpha = Alpha { alphaName :: String }
data Bravo = Bravo { bravoTag  :: String }

-- Mutually recursive top-level functions — Haskell handles this
-- natively (all top-level bindings are in one letrec group).
spawnBravo :: Alpha -> Bravo
spawnBravo a = Bravo (alphaName a ++ "/b")

bounceToAlpha :: Bravo -> String
bounceToAlpha b = describe (Alpha ("bounce-from-" ++ bravoTag b))

describe :: Alpha -> String
describe a = "Alpha(" ++ alphaName a ++ ")"

kickOff :: String
kickOff = bounceToAlpha (spawnBravo (Alpha "root"))
