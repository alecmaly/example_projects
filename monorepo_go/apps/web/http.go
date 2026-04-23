package main

// net/http framework idioms: HandleFunc, method dispatch, middleware
// chain via decorator pattern, context.WithValue, http.HandlerFunc
// conversion, ServeMux routing.

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"
)

type ctxKey string

const userIDKey ctxKey = "user_id"

type HTTPUser struct {
	ID    int    `json:"id"`
	Email string `json:"email"`
}

type UserStore struct {
	byID map[int]HTTPUser
}

func NewUserStore() *UserStore {
	return &UserStore{byID: map[int]HTTPUser{
		1: {ID: 1, Email: "alice@example.com"},
		2: {ID: 2, Email: "bob@example.com"},
	}}
}

func (s *UserStore) Get(id int) (HTTPUser, bool) {
	u, ok := s.byID[id]
	return u, ok
}

// --- middleware: logging ---
func withLogging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
	})
}

// --- middleware: auth injection ---
func withAuth(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		tok := r.Header.Get("Authorization")
		if tok == "" {
			http.Error(w, "unauthorized", http.StatusUnauthorized)
			return
		}
		ctx := context.WithValue(r.Context(), userIDKey, 1)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// --- handler: GET /users/:id ---
func (s *UserStore) getUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	parts := strings.Split(strings.TrimPrefix(r.URL.Path, "/users/"), "/")
	id, err := strconv.Atoi(parts[0])
	if err != nil {
		http.Error(w, "bad id", http.StatusBadRequest)
		return
	}
	u, ok := s.Get(id)
	if !ok {
		http.NotFound(w, r)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(u)
}

// --- handler: POST /users ---
func (s *UserStore) createUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	var body HTTPUser
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		http.Error(w, "bad body", http.StatusBadRequest)
		return
	}
	uid, _ := r.Context().Value(userIDKey).(int)
	fmt.Printf("creator=%d new=%s\n", uid, body.Email)
	s.byID[body.ID] = body
	w.WriteHeader(http.StatusCreated)
	_ = json.NewEncoder(w).Encode(body)
}

func runHTTPServer() {
	store := NewUserStore()
	mux := http.NewServeMux()
	mux.HandleFunc("/users/", store.getUserHandler)
	mux.Handle("/users", withAuth(http.HandlerFunc(store.createUserHandler)))
	wrapped := withLogging(mux)
	srv := &http.Server{Addr: ":8080", Handler: wrapped, ReadTimeout: 5 * time.Second}
	log.Fatal(srv.ListenAndServe())
}
