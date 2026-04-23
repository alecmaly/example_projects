module MonoShared
  module ScopesNs
    class Widget                              # S14.Widget.def
      attr_reader :label
      def initialize(label); @label = label; end
    end
  end
end
