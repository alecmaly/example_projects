module Scopes.Ns where

data Widget = Widget { widgetLabel :: String }       -- S14.Widget.def

mkWidget :: String -> Widget
mkWidget = Widget

constant :: String
constant = "shared-constant"
