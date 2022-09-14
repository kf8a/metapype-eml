# frozen_string_literal: true

require "json"

data = File.read("src/metapype/eml/rules.json")

json = JSON.parse(data)

newjson = {}
json.each do |datum|
  name, rules = datum
  attributes, children, content = rules
  attributes = attributes.collect { |key, value| { key => value } }

  newjson.store(name,[attributes, children, content])
end

puts JSON.pretty_generate(newjson)
