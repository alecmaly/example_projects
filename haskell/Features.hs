{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE DeriveFunctor #-}

-- Haskell feature coverage: ADTs, type classes, monads, lazy eval,
-- pattern matching, records, newtype, guards, where-clauses.

module Features
  ( Shape(..)
  , area
  , Greeter(..)
  , FancyGreeter(..)
  , shoutGreet
  , fibs
  , classify
  , runFeatureDemo
  ) where

-- ADT — sum type with parameters.
data Shape
  = Circle Double
  | Square Double
  | Rectangle { width :: Double, height :: Double }
  deriving (Show)

area :: Shape -> Double
area (Circle r)                 = 3.14159 * r * r
area (Square s)                 = s * s
area (Rectangle w h)            = w * h

-- Type class — ad-hoc polymorphism.
class Greeter a where
  greet :: a -> String

instance Greeter String where
  greet s = "hello, " ++ s

instance Greeter Int where
  greet n = "number " ++ show n

-- Superclass constraint — FancyGreeter requires Greeter,
-- so any instance of FancyGreeter can also use `greet`.
class Greeter a => FancyGreeter a where
  fancyGreet :: a -> String
  fancyGreet x = ">>> " ++ greet x ++ " <<<"

instance FancyGreeter String
instance FancyGreeter Int where
  fancyGreet n = "*** " ++ greet n ++ " ***"

-- Constraint on a function signature (context).
shoutGreet :: (FancyGreeter a) => a -> String
shoutGreet x = fancyGreet x ++ "!"

-- Lazy infinite list.
fibs :: [Int]
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

-- Guards.
classify :: Int -> String
classify n
  | n < 0      = "negative"
  | n == 0     = "zero"
  | otherwise  = "positive"

-- Functor instance via deriving.
newtype Boxed a = Boxed { unbox :: a } deriving (Functor)

-- do-notation — IO monad.
runFeatureDemo :: IO ()
runFeatureDemo = do
  putStrLn (greet ("world" :: String))
  putStrLn (greet (42 :: Int))
  putStrLn (shoutGreet ("haskell" :: String))   -- via superclass constraint
  putStrLn (shoutGreet (7 :: Int))
  putStrLn ("area circle = " ++ show (area (Circle 2)))
  putStrLn ("first 10 fibs = " ++ show (take 10 fibs))
  putStrLn ("classify(-1) = " ++ classify (-1))
  let b = fmap (+1) (Boxed 5)
  putStrLn ("boxed = " ++ show (unbox b))
