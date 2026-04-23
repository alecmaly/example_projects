{-# LANGUAGE ScopedTypeVariables #-}

module Casts where

import           Data.Maybe       (fromMaybe)
import           Text.Read        (readMaybe)
import qualified Data.Typeable    as T

-- 1. Numeric widening / narrowing via fromIntegral.
widen :: Int -> Double
widen = fromIntegral

-- 2. read :: String -> T via Read class (partial).
parseInt :: String -> Int
parseInt = read

-- 3. Total-parse via readMaybe.
safeParse :: String -> Maybe Int
safeParse = readMaybe

-- 4. show :: T -> String via Show class.
showAny :: Show a => a -> String
showAny = show

-- 5. Enum conversions.
charCode :: Char -> Int
charCode = fromEnum
codeToChar :: Int -> Char
codeToChar = toEnum

-- 6. Typeable cast (reflective, rarely used).
castAny :: forall a b. (T.Typeable a, T.Typeable b) => a -> Maybe b
castAny = T.cast

-- 7. fromRational / toRational.
ratioDemo :: Double -> Rational
ratioDemo = toRational

runCastsDemo :: IO ()
runCastsDemo = do
  putStrLn (showAny (widen 3))
  putStrLn (showAny (parseInt "42"))
  putStrLn (showAny (safeParse "not-a-number"))
  putStrLn (showAny (charCode 'A'))
  putStrLn (showAny (codeToChar 97))
  putStrLn (showAny (castAny (5 :: Int) :: Maybe Int))
  putStrLn (showAny (ratioDemo 3.14))
