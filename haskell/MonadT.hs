{-# LANGUAGE GADTs #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE FlexibleInstances #-}

-- Haskell advanced feature coverage: GADTs, type families, monad transformer
-- stacks, and do-notation in a non-IO monad. Parser-only fixture; imports
-- may reference packages that aren't installed.

module MonadT where

import Control.Monad.Reader
import Control.Monad.Except
import Control.Monad.IO.Class

-- --- GADT: expression language with type-indexed constructors.
data Expr a where
  IntE  :: Int -> Expr Int
  BoolE :: Bool -> Expr Bool
  Add   :: Expr Int -> Expr Int -> Expr Int
  If    :: Expr Bool -> Expr a -> Expr a -> Expr a

eval :: Expr a -> a
eval (IntE n)     = n
eval (BoolE b)    = b
eval (Add x y)    = eval x + eval y
eval (If c t e)   = if eval c then eval t else eval e

-- --- Type family: element type of a container.
type family Elem c
type instance Elem [a]       = a
type instance Elem (Maybe a) = a

-- --- Monad transformer stack: ExceptT String (ReaderT AppConfig IO) Int.
data AppConfig = AppConfig { prefix :: String }

runStep :: ExceptT String (ReaderT AppConfig IO) Int
runStep = do
  cfg <- ask
  liftIO (putStrLn (prefix cfg ++ ": starting"))
  if null (prefix cfg)
    then throwError "empty prefix"
    else return 42

-- --- do-notation chain in a non-IO monad (Either).
safeDiv :: Int -> Int -> Either String Int
safeDiv _ 0 = Left "divide by zero"
safeDiv x y = Right (x `div` y)

computeEither :: Int -> Int -> Int -> Either String Int
computeEither a b c = do
  let doubled = a * 2
  q <- safeDiv doubled b
  r <- Right q >>= \v -> safeDiv v c
  let shifted = r + 1
  return shifted
