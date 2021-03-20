console.log("Sanity check!");

// Get Stripe publishable key
fetch("/config")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);

  var elements = stripe.elements();
  var style = {
      base: {
          // Add your base input styles here. For example:
          fontSize: '16px',
          color: '#32325d',
      },
  };
  // Create an instance of the card Element.
  var card = elements.create('card', {style: style});

  let paymentIntent;

  // Add an instance of the card Element into the `card-element` <div>.
  card.mount('#card-element');

  //charge = get_current_cart();
  const paymentRequest = stripe.paymentRequest({
    country: charge.stripeCountry,
    currency: charge.currency,
    total: {
      label: 'Total',
      amount: charge.price_paid(),
    },
    requestShipping: true,
    requestPayerEmail: true,
  });


  var form = document.getElementById('payment-form');
  form.addEventListener('submit', function(event) {
      event.preventDefault();

      payNow()
  });
  function payNow(){
      stripe.createToken(card).then(function(result) {
          if (result.error) {
              // Inform the customer that there was an error.
              var errorElement = document.getElementById('card-errors');
              errorElement.textContent = result.error.message;
          } else {
              // Send the token to your server.
              stripeTokenHandler(result.token);
          }
      });
  }
  function stripeTokenHandler(token) {
    // Insert the token ID into the form so it gets submitted to the server
    var form = document.getElementById('payment-form');
    var hiddenInput = document.createElement('input');
    hiddenInput.setAttribute('type', 'hidden');
    hiddenInput.setAttribute('name', 'stripeToken');
    hiddenInput.setAttribute('value', token.id);
    form.appendChild(hiddenInput);

    // Submit the form
    form.submit();
}
// Callback when a payment method is created.


});
