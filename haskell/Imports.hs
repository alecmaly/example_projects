module Imports where

-- 1. Unqualified plain import.
import Data.List

-- 2. Qualified — forces dot-prefix.
import qualified Data.Map.Strict as M

-- 3. Explicit symbol list.
import Data.Maybe (fromMaybe, isJust)

-- 4. Hiding.
import Prelude hiding (lookup)

-- 5. Aliased qualified.
import qualified Data.Set as S

-- 6. Re-export (exported from this module even though defined elsewhere).
--    See the module header of Features.hs for the more standard form.

run :: IO ()
run = do
    let m  = M.fromList [(1 :: Int, "one"), (2, "two")]
    let s  = S.fromList [1, 2, 3]
    putStrLn ("size " ++ show (M.size m) ++ ", set " ++ show (S.size s))
    putStrLn ("fromMaybe " ++ fromMaybe "no" (Just "yes"))
    putStrLn ("isJust(Just 1) = " ++ show (isJust (Just (1 :: Int))))
    putStrLn ("sorted " ++ show (sort [3, 1, 2]))
