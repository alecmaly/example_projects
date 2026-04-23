-- Labeled scope test cases for Haskell. See SCOPE_TEST_SPEC.md.
-- N/A: S03/S05/S07 (no mutation without IORef/MVar), S12 (no class-static
-- distinction), S13 (type class methods substitute for inheritance).

module Scopes where

import qualified Scopes.Ns as NS            -- S14.import

moduleVar :: String                         -- S04.def
moduleVar = "mod-initial"

s01Local :: IO ()
s01Local = do
  let localA = "S01.local"                  -- S01.def
  putStrLn localA                           -- S01.read

s02ClosureRead :: IO ()
s02ClosureRead = do
  let outerA = "S02.outer"                  -- S02.outer.def
  let inner = putStrLn outerA               -- S02.inner.read (captured)
  inner

s06CrossRead :: String
s06CrossRead = NS.constant                  -- S06.read

s08Shadowing :: IO ()
s08Shadowing = do
  let moduleVar = "shadowed"                -- S08.shadow.def
  putStrLn moduleVar                        -- S08.shadow.read

-- S11: record-field vs function-arg.
data ScopeBase = ScopeBase { x :: Int }
readInstance :: Int -> ScopeBase -> Int
readInstance x b = x + Scopes.x b           -- S11.param.read + S11.instance.read

s14Qualified :: String
s14Qualified = NS.widgetLabel (NS.mkWidget "hi")  -- S14.read

runScopeDemo :: IO ()
runScopeDemo = do
  s01Local
  s02ClosureRead
  putStrLn s06CrossRead
  s08Shadowing
  print (readInstance 100 (ScopeBase 42))
  putStrLn s14Qualified
